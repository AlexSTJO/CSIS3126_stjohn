import boto3
import boto3.exceptions

class OrcaRunner:
    def __init__(self, session):
        self.session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region_name
        )
        self.region_name = region_name
        self.ec2_client = self.session.client('ec2')
        self.ssm_client = self.session.client('ssm')
    def invoke_command(self, bucket_name, file_path):
        ssm_client = self.ssm_client

        script_s3_path = f"s3://{bucket_name}/scripts/{file_path}"

        commands = [
            f"aws s3 cp {script_s3_path} /tmp/script.py",
            'python3 /tmp/script.py'
        ]

        response = ssm_client.send_command(
            InstanceIds=[ec2_instance],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': commands},
        )

        command_id = response['Command']['CommandId']
        print(f"Command sent. Command ID: {command_id}")


        time.sleep(3)
        while True:
            output = ssm_client.list_command_invocations(
                CommandId=command_id,
                InstanceId=ec2_instance,
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
    
    def create_project(self):
        # Creates a new folder in s3 where scripts will be stored
