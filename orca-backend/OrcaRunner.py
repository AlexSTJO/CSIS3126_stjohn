import boto3
import botocore.exceptions
import csv
import json
import time
from datetime import datetime


class OrcaRunner:
    def __init__(self, session, bucket_name, instance_id, project_name):
        self.ec2_client = session.client('ec2')
        self.ssm_client = session.client('ssm')
        self.s3_client = session.client('s3') 
        self.bucket_name = bucket_name
        self.instance_id = instance_id
        self.project_name = project_name
        self.manifest_data = self.read_manifest()
        

    def read_manifest(self):
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=f"{self.project_name}/execution-manifest.json"
            )
            manifest_content = response["Body"].read().decode("utf-8")
            return json.loads(manifest_content)
        except botocore.exceptions.ClientError as e:
            print(f"[ERROR] Failed to read manifest: {e}")
            raise

    def stream_pipeline(self):
        run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        yield f"[PIPELINE] Run ID: {run_id}\n"

        ordered_tasks = sorted(self.manifest_data['Tasks'], key=lambda task: task['Order'])

        yield "[PIPELINE] Bootstrapping instance...\n"
        bootstrap_command_id = self.bootstrap_instance()
        for output in self.stream_command_output(bootstrap_command_id):
            yield f"[BOOTSTRAP] {output}"

        for index, task in enumerate(ordered_tasks):
            yield f"\n[TASK {index + 1}] Starting {task['Name']}...\n"
            command_id = self.invoke_script(task, run_id=run_id, task_index=index, return_only_command_id=True)

            for chunk in self.stream_command_output(command_id):
                yield chunk

    def bootstrap_instance(self):
        commands = [
            'rm -rf /tmp',
            'mkdir -p /tmp/orca',
            'yum install -y jq python3 python3-pip',
            'python3 -m venv /tmp/venv',
            f"aws s3 cp s3://{self.bucket_name}/{self.project_name}/dependencies.txt /tmp/orca/requirements.txt || true",
            '/tmp/venv/bin/pip install --upgrade pip',
            '/tmp/venv/bin/pip install -r /tmp/orca/requirements.txt || true',
            '/tmp/venv/bin/pip install "urllib3<2.0" "requests<3.0"'
        ]
        response = self.ssm_client.send_command(
            InstanceIds=[self.instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': commands},
        )

        command_id = response['Command']['CommandId']
        print(f"[BOOTSTRAP] Command sent. ID: {command_id}")
        return command_id

    def invoke_script(self, task, run_id, task_index, return_only_command_id=False):
        file_name = task["Name"]
        inputs = task.get("Inputs", [])
        script_base = file_name.replace('.py', '')
        outputs_path = f"s3://{self.bucket_name}/{self.project_name}/outputs/{run_id}/{script_base}/"
        log_path = f"s3://{self.bucket_name}/{self.project_name}/logs/{run_id}/log-{file_name}.json"
        script_path = f"s3://{self.bucket_name}/{self.project_name}/{file_name}"

        commands = [
            f"aws s3 cp {script_path} /tmp/orca/script.py"
        ]
        commands += self.resolve_input_downloads(run_id, task_index, inputs)
        commands += [
            'source /tmp/venv/bin/activate',
            'cd /tmp/orca',
            '/tmp/venv/bin/python script.py > out.txt 2> err.txt; EXIT_CODE=$?',
            'if [ -f out.txt ]; then echo "[SCRIPT] Script Output"; cat out.txt; fi',
            'if [ -f err.txt ]; then echo "[SCRIPT] Script Errors"; cat err.txt; fi',
            'echo "[LOG] Output complete"', 
            'python3 -c \'import os, json; '
            'f = open("/tmp/orca/log.json", "w"); '
            'json.dump({'
            '"stdout": open("out.txt").read(), '
            '"stderr": open("err.txt").read(), '
            '"exit_code": int(os.environ.get("EXIT_CODE", "1"))'
            '}, f)\'',
            f'aws s3 cp /tmp/orca/log.json {log_path}',
            f'for file in $(find /tmp/orca -type f ! -name "log.json" ! -name "script.py" ! -name "requirements.txt" ! -name "err.txt" ! -name "out.txt"); do '
            f'aws s3 cp "$file" {outputs_path}$(basename $file); done'
        ]
        response = self.ssm_client.send_command(
            InstanceIds=[self.instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': commands},
        )

        command_id = response['Command']['CommandId']
        print(f"[SCRIPT] Command sent. ID: {command_id} for task: {file_name}")

        if return_only_command_id:
            return command_id
        else:
            return self._wait_for_command(command_id)

    def stream_command_output(self, command_id):
        seen_output = ""
        while True:
            result = self.ssm_client.list_command_invocations(
                CommandId=command_id,
                InstanceId=self.instance_id,
                Details=True
            )

            if not result['CommandInvocations']:
                time.sleep(1)
                continue

            invocation = result['CommandInvocations'][0]
            status = invocation['Status']
            output = invocation['CommandPlugins'][0].get('Output', '')

            if output != seen_output:
                new_chunk = output[len(seen_output):]
                seen_output = output
                yield new_chunk

            if status in ['Success', 'Cancelled', 'Failed', 'TimedOut']:
                yield f"\n[STATUS] {status}\n"
                break

            time.sleep(2)

    def _wait_for_command(self, command_id):
        time.sleep(2)
        while True:
            result = self.ssm_client.list_command_invocations(
                CommandId=command_id,
                InstanceId=self.instance_id,
                Details=True
            )

            if not result['CommandInvocations']:
                time.sleep(2)
                continue

            status = result['CommandInvocations'][0]['Status']
            output = result['CommandInvocations'][0]['CommandPlugins'][0]['Output']

            if status in ['Pending', 'InProgress']:
                time.sleep(2)
                continue

            return output

    def resolve_input_downloads(self, run_id, current_task_index, input_files):
        download_commands = []

        previous_tasks = self.manifest_data['Tasks'][:current_task_index]

        for input_file in input_files:
            found = False
            for task in reversed(previous_tasks):  
                task_folder = task['Name'].replace('.py', '')
                s3_path = f"s3://{self.bucket_name}/{self.project_name}/outputs/{run_id}/{task_folder}/{input_file}"
                cmd = f"aws s3 cp {s3_path} /tmp/orca/{input_file} || true"
                download_commands.append(cmd)
                found = True
                break  

            if not found:
                print(f"[WARN] Input file '{input_file}' not found in earlier task outputs (will still attempt fetch).")

        return download_commands




def pull_creds():
    with open('../secrets.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            creds = {'access_key': row['Access key ID'],
                     'secret_access_key': row['Secret access key']}

    return creds

if __name__ == "__main__":
    creds = pull_creds()

    session = boto3.Session(
        aws_access_key_id=creds["access_key"],
        aws_secret_access_key=creds["secret_access_key"],
        region_name="us-east-2"
    )
    
    runner = OrcaRunner(session, instance_id = "i-018d124ff372e4da0", bucket_name="orca-s3-1738617758188", project_name="weird")
    runner.handle_runtime()

