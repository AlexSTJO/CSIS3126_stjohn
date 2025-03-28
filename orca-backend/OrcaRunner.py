import boto3
import botocore.exceptions
import csv
import json
import time
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


    def handle_manifest(self):
        ordered_tasks = sorted(self.manifest_data['Tasks'], key=lambda task: task['Order']) 

        for task in ordered_tasks:
            self.invoke_script(task["Name"])


        



    def invoke_script(self, file_name):
        ssm_client = self.ssm_client

        script_s3_path = f"s3://{self.bucket_name}/{self.project_name}/{file_name}"

        commands = [
            f"aws s3 cp {script_s3_path} /tmp/script.py",
            'python3 /tmp/script.py'
        ]

        response = ssm_client.send_command(
            InstanceIds=[self.instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': commands},
        )

        command_id = response['Command']['CommandId']
        print(f"Command sent. Command ID: {command_id}")


        time.sleep(3)
        while True:
            output = ssm_client.list_command_invocations(
                CommandId=command_id,
                InstanceId=self.instance_id,
                Details=True
            )

            if output['CommandInvocations']:
                    status = output['CommandInvocations'][0]['Status']
                    if status in ['InProgress', 'Pending']:
                        print(f"Command is still running. Status: {status}")
                        time.sleep(2)
                        continue
                    elif status == 'Success':
                        print('Command executed successfully.')
                        stdout = output['CommandInvocations'][0]['CommandPlugins'][0]['Output']
                        print('Command Output:')
                        print(stdout)
                        return stdout
                    else:
                        print(f"Command failed with status: {status}")
                        stderr = output['CommandInvocations'][0]['CommandPlugins'][0]['Output']
                        print('Error Output:')
                        print(stderr)
                        return stderr


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
    runner.handle_manifest()

