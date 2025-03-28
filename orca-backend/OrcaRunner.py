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
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=f"{self.project_name}/execution-manifest.json")
        manifest_content = response["Body"].read().decode("utf-8")
        manifest_data = json.loads(manifest_content)
        return manifest_data


    def handle_runtime(self):
        run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        print(f"[PIPELINE] Run ID: {run_id}")

        ordered_tasks = sorted(self.manifest_data['Tasks'], key=lambda task: task['Order']) 
        self.bootstrap_instance()

        for index, task in enumerate(ordered_tasks):
            self.invoke_script(task, run_id=run_id, task_index=index)


    def bootstrap_instance(self):
        commands = [
            'rm -rf /tmp/orca',                     
            'mkdir -p /tmp/orca',
            'yum install -y jq python3 python3-pip',
            'python3 -m venv /tmp/venv',
            f"aws s3 cp s3://{self.bucket_name}/{self.project_name}/dependencies.txt /tmp/orca/requirements.txt || true",
            '/tmp/venv/bin/pip install --upgrade pip',
            '/tmp/venv/bin/pip install -r /tmp/orca/requirements.txt || true',
            'rm /tmp/orca/requirements.txt'
        ]

        response = self.ssm_client.send_command(
            InstanceIds=[self.instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': commands},
        )

        command_id = response['Command']['CommandId']
        print(f"[BOOTSTRAP] Command sent. ID: {command_id}")

        return self._wait_for_command(command_id)
   

    def invoke_script(self, task, run_id, task_index):
        file_name = task["Name"]
        inputs = task.get("Inputs", [])
        script_base = file_name.replace('.py', '')
        outputs_path = f"s3://{self.bucket_name}/{self.project_name}/outputs/{run_id}/{script_base}/"
        log_path = f"s3://{self.bucket_name}/{self.project_name}/logs/{run_id}/log-{file_name}.json"
        script_path = f"s3://{self.bucket_name}/{self.project_name}/{file_name}"

        commands = []

        commands.append(f"aws s3 cp {script_path} /tmp/orca/script.py")

        commands += self.resolve_input_downloads(run_id, task_index, inputs)

        commands += [
            'source /tmp/venv/bin/activate',
            'output=$(/tmp/venv/bin/python /tmp/orca/script.py 2>&1); exit_code=$?',
            'log=$(jq -n --arg out "$output" --argjson code "$exit_code" '
            '\'{"stdout": $out, "stderr": "", "exit_code": $code}\')',
            'echo "$log" > /tmp/orca/log.json',
            f"aws s3 cp /tmp/orca/log.json {log_path}",

            f'for file in $(find /tmp/orca -type f ! -name "script.py" ! -name "log.json"); do '
            f'aws s3 cp "$file" {outputs_path}$(basename $file); done'
        ]

        response = self.ssm_client.send_command(
            InstanceIds=[self.instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': commands},
        )

        command_id = response['Command']['CommandId']
        print(f"[SCRIPT] Command sent. ID: {command_id} for task: {file_name}")

        return self._wait_for_command(command_id)

    def _wait_for_command(self, command_id):
    
        time.sleep(2)
        while True:
            result = self.ssm_client.list_command_invocations(
                CommandId=command_id,
                InstanceId=self.instance_id,
                Details=True
            )

            if not result['CommandInvocations']:
                print("No output yet, waiting...")
                time.sleep(2)
                continue

            status = result['CommandInvocations'][0]['Status']
            if status in ['Pending', 'InProgress']:
                print(f"Command running... Status: {status}")
                time.sleep(2)
                continue

            output = result['CommandInvocations'][0]['CommandPlugins'][0]['Output']
            print(f"Command finished with status: {status}")
            print("Output:\n", output)
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

