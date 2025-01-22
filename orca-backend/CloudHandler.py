import csv
import boto3
import time

# Session Creator
def session_create(access_key, secret_access_key,):
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key= secret_access_key,
        region_name='us-east-2'
    )

    return session

# Uploads File to s3 bucket
def upload_file(session, file_path, bucket_name):
    s3_key = f"scripts/{file_path}"

    s3_client = session.client("s3")

    response = s3_client.upload_file(Filename = file_path,Bucket = bucket_name,Key=s3_key)

    return response

# Creates EC2 Connection, Runs Script in EC2, and stores in stdout
def ec2_connect(session, bucket_name, ec2_instance, file_path):
    ssm_client = session.client('ssm')

    script_s3_path = f"s3://{bucket_name}/scripts/{file_path}"

    commands = [
        f"aws s3 cp {script_s3_path} /tmp/script.py",
        "python3 /tmp/script.py"
    ]

    response = ssm_client.send_command(
        InstanceIds=[ec2_instance],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands},
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
                    print("Command executed successfully.")
                    stdout = output['CommandInvocations'][0]['CommandPlugins'][0]['Output']
                    print("Command Output:")
                    print(stdout)
                    return stdout
                else:
                    print(f"Command failed with status: {status}")
                    stderr = output['CommandInvocations'][0]['CommandPlugins'][0]['Output']
                    print("Error Output:")
                    print(stderr)
                    return stderr

if __name__ == "__main__":
    secret_csv = '../secrets.csv'
    
    with open(secret_csv, mode='r',encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        secrets = next(reader)

    access_key = secrets['Access key ID']
    secret_access_key = secrets['Secret access key']
    bucket = secrets["Bucket"]
    ec2_instance = secrets["Instance ID"]

    session = session_create(access_key, secret_access_key)

    file_path = "test.py"

    upload_file(file_path=file_path,session=session,bucket_name=bucket)
    ec2_connect(session=session, bucket_name=bucket, ec2_instance=ec2_instance,file_path=file_path)


