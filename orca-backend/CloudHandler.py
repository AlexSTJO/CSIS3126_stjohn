import csv
import boto3
import time
import os
# Session Creator
def session_create(access_key, secret_access_key):
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

# Gets Cloud Credentials For Link
def get_db_credentials():
    client = boto3.client('secretsmanager', region_name='us-east-2')

    try:
        secret_name = os.getenv("DB_SECRET_NAME")
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return {
            "user": secret["username"],
            "password": secret["password"],
        }
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
        raise
# Gets Encryption Key from Secrets Manager
def get_encryption_key(encryption_key_id):
    secret_name = os.getenv("SECRET_NAME")
    if secret_name != "":

        client = boto3.client('secretsmanager', region_name='us-east-2')
        
        try:
            secret_name = "orca/secrets"
            response = client.get_secret_value(SecretId=secret_name)
            secret = json.loads(response['SecretString'])
            return secret[encryption_key_id]
        except Exception as e:
            print(f"Error retrieving secrets: {e}")
            raise
    else:
        return os.getenv("E_KEY")
    


def cloud_setup(bucket_name, ec2_name, access_key, secret_access_key, region_name):
    session = session_create(access_key, secret_access_key)
    
    bucket_success = bucket_create(session, bucket_name, region_name)
    

def bucket_create(session, bucket_name, region_name):

    s3_client = session.client("s3", region_name=region_name)
    
    try:
        response = s3_client.create_bucket(Bucket=bucket_name)
        print("Bucket created successfully", response)

    except botocore.exceptions.ClientError as e:
        error_code  = e.response["Error"]["Code"]

    if error_code == "BucketAlreadyExists":
        print(f"Error: The bucket name '{bucket_name}' is already taken and owned by another AWS account.")
    elif error_code == "BucketAlreadyOwnedByYou":
        print(f"Error: The bucket '{bucket_name}' already exists in your account.")
    else:
        print(f"Unexpected Error: {e}")


def ec2_create(session, region_name):
    ec2_client = session.client("ec2", region_name=region_name)
        
    # Create security group
    create_and_configure_vpc(ec2_client, region_name)
    '''try:
        response = ec2_client.create_security_group(
        GroupName='orca-sg',
        Description='Security Group for Orca EC2',
        )
    except botocore.exceptions.ClientError as e:
        print(f"Error: {e}")'''
    # Create IAM Role
    # Create Key Pair
    # Create EC2

def create_and_configure_vpc(ec2_client, region_name):
    try:
        response = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
        vpc_id = response["Vpc"]["VpcID"]
        print(f"VPC Created: {vpc_id}")
        
        ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
        ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
    except botocore.exceptions.ClientError as e:
        print(f"Error: {e}")

    try:
        igw_response = ec2_client.create_internet_gateway()
        internet_gateway_id = igw_response['InternetGateway']['InternetGatewayId']
        print(f"Internet Gateway created: {internet_gateway_id}")
       
        # Create a subnet in the VPC
        subnet_response = ec2_client.create_subnet(
            VpcId=vpc_id,
            CidrBlock='9.0.1.0/24',
            AvailabilityZone=f'{region_name}a'  
        )

        subnet_id = subnet_response['Subnet']['SubnetId']
        print(f"Subnet created: {subnet_id}")
        
        route_table_response = ec2_client.create_route_table(VpcId=vpc_id)
        route_table_id = route_table_response["RouteTable"]["RouteTableId"]
        print(f"Route table created: {route_table_id}")
        
        ec2_client.create_route(
            RouteTableId=route_table_id,
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=internet_gateway_id
        )
        
        ec2_client.associate_route_table(SubnetID=subnet_id, RouteTableId=route_table_id)
        print("Route table associated with the subnet")

        ec2_client.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={'Value': True})
        
        print("Auto-assign public IP enabled for the subnet.")
        print("VPC Configurations Done")

    except botocore.exceptions.ClientError as e:
        print("Error: {e}")

          
        
 
def pull_creds():
    with open('../secrets.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            creds = {"access_key": row["Access key ID"],
                     "secret_access_key": row["Secret access key"]}

    return creds

if __name__ == "__main__":
    creds = pull_creds()
    session_create(creds["access_key"], creds["secret_access_key"])


