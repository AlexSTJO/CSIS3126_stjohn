import csv
import boto3
import time
import os
import boto3
import botocore.exceptions
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

    s3_client = session.client('s3')

    response = s3_client.upload_file(Filename = file_path,Bucket = bucket_name,Key=s3_key)

    return response

# Creates EC2 Connection, Runs Script in EC2, and stores in stdout
def ec2_connect(session, bucket_name, ec2_instance, file_path):
    ssm_client = session.client('ssm')

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

# Gets Cloud Credentials For Link
def get_db_credentials():
    client = boto3.client('secretsmanager', region_name='us-east-2')

    try:
        secret_name = os.getenv('DB_SECRET_NAME')
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return {
            'user': secret['username'],
            'password': secret['password'],
        }
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
        raise
# Gets Encryption Key from Secrets Manager
def get_encryption_key(encryption_key_id):
    secret_name = os.getenv('SECRET_NAME')
    if secret_name != '':

        client = boto3.client('secretsmanager', region_name='us-east-2')
        
        try:
            secret_name = 'orca/secrets'
            response = client.get_secret_value(SecretId=secret_name)
            secret = json.loads(response['SecretString'])
            return secret[encryption_key_id]
        except Exception as e:
            print(f"Error retrieving secrets: {e}")
            raise
    else:
        return os.getenv('E_KEY')
    


def cloud_setup(bucket_name, ec2_name, access_key, secret_access_key, region_name):
    session = session_create(access_key, secret_access_key)
    
    bucket_success = bucket_create(session, bucket_name, region_name)
    

def bucket_create(session, bucket_name, region_name):

    s3_client = session.client('s3', region_name=region_name)
    
    try:
        response = s3_client.create_bucket(Bucket=bucket_name)
        print('Bucket created successfully', response)

    except botocore.exceptions.ClientError as e:
        error_code  = e.response['Error']['Code']

    if error_code == 'BucketAlreadyExists':
        print(f"Error: The bucket name {bucket_name} is already taken and owned by another AWS account.")
    elif error_code == 'BucketAlreadyOwnedByYou':
        print(f"Error: The bucket {bucket_name} already exists in your account.")
    else:
        print(f"Unexpected Error: {e}")


def ec2_create(session, region_name):
    ec2_client = session.client('ec2', region_name=region_name)
    existing_resources = resource_existence(ec2_client)
    existing_resources = create_and_configure_vpc(ec2_client, region_name, existing_resources)
    if existing_resources['KeyPair'] == None:
        create_key_pair(ec2_client)
    else:
        print(f"Key Pair Exists: {existing_resources['KeyPair']}")

    if existing_resources['SecurityGroup'] == None:
        existing_resources['SecurityGroup']= create_security_group(ec2_client, existing_resources['Vpc'])
    else:
        print(f"Security Group Exists {existing_resources['SecurityGroup']}")
    
    try:
        if existing_resources['Ec2'] == None:
            ssm_client = session.client('ssm', region_name='us-east-2')
            ami_response = ssm_client.get_parameter(
                Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
            )
            amazon_linux_ami_id = ami_response['Parameter']['Value']

            instance_response = ec2_client.run_instances(
                ImageId=amazon_linux_ami_id,  # Replace with a valid AMI ID
                InstanceType='t2.micro',  # Change as needed
                KeyName='orca-ec2-key',
                SecurityGroupIds=[existing_resources['SecurityGroup']],
                SubnetId=existing_resources['Subnet'],
                MinCount=1,
                MaxCount=1,
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': 'orca-runner'}]
                    }
                ]
            )

            existing_resources['Ec2'] = instance_response['Instances'][0]['InstanceId']
            print(f"EC2 Instance launched: {existing_resources['Ec2']}")
        else:
            print(f"Ec2 Instance Exists: {existing_resources['Ec2']}")
    except botocore.exceptions.ClientError as e:
        print(f"Error: {e}")

def create_and_configure_vpc(ec2_client, region_name, existing_resources):
    try:
        if existing_resources['Vpc'] == None:
            response = ec2_client.create_vpc(CidrBlock='10.0.0.0/24',
                TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': [
                    {'Key': 'Name', 'Value': 'Orca'}
                ]
            }
            ])
            existing_resources['Vpc'] = response['Vpc']['VpcId']
            print(f"VPC Created: {existing_resources['Vpc']}")
            
            ec2_client.modify_vpc_attribute(VpcId=existing_resources['Vpc'], EnableDnsSupport={'Value': True})
            ec2_client.modify_vpc_attribute(VpcId=existing_resources['Vpc'], EnableDnsHostnames={'Value': True})
        else:
            print(f"VPC Exists: {existing_resources['Vpc']}")

        if existing_resources['InternetGateway'] == None:
            igw_response = ec2_client.create_internet_gateway()
            existing_resources['InternetGateway'] = igw_response['InternetGateway']['InternetGatewayId']
            print(f"Internet Gateway created: {existing_resources['InternetGateway']}")

            ec2_client.attach_internet_gateway(
            InternetGatewayId=existing_resources['InternetGateway'],
            VpcId=existing_resources['Vpc']
            )
        else:
            print(f"Internet Gateway Exists: {existing_resources['InternetGateway']}")


        if existing_resources['Subnet'] == None: 
            subnet_response = ec2_client.create_subnet(
                VpcId=existing_resources['Vpc'],
                CidrBlock='10.0.0.0/26',
                AvailabilityZone=f"{region_name}a"  
            )

            existing_resources['Subnet'] = subnet_response['Subnet']['SubnetId']
            print(f"Subnet created: {existing_resources['Subnet']}")
        else:
            print(f"Subnet Exists: {existing_resources['Subnet']}")
        if existing_resources['RouteTable'] == None:
            route_table_response = ec2_client.create_route_table(VpcId=existing_resources['Vpc'])
            existing_resources['RouteTable'] = route_table_response['RouteTable']['RouteTableId']
            print(f"Route table created: {existing_resources['RouteTable']}")
        
            ec2_client.create_route(
                RouteTableId=existing_resources['RouteTable'],
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=existing_resources['InternetGateway']
            )
            
            ec2_client.associate_route_table(SubnetId=existing_resources['Subnet'], RouteTableId=existing_resources['RouteTable'])
            print('Route table associated with the subnet')

            ec2_client.modify_subnet_attribute(SubnetId=existing_resources['Subnet'], MapPublicIpOnLaunch={'Value': True})
            print('Auto-assign public IP enabled for the subnet.')
        else:
            print(f"Route Table Exists: {existing_resources['RouteTable']}")
        print('VPC Configurations Done')
        return existing_resources

    except botocore.exceptions.ClientError as e:
        print(f"Error: {e}")

def create_key_pair(ec2_client):   
    try:
        key_pair_response = ec2_client.create_key_pair(KeyName='orca-ec2-key')
        private_key = key_pair_response['KeyMaterial']

        with open('orca-ec2-key.pem', 'w') as key_file:
            key_file.write(private_key)
        print('Key pair created and saved as orca-ec2-key.pem')

    except botocore.exceptions.ClientError as e:
        print(f"Error as {e}")

def create_security_group(ec2_client,vpc_id):
    try:
        security_group_response = ec2_client.create_security_group(
            GroupName='orca-runner-security-group',
            Description='Security group for orca-runner to allow SSM and SSH access',
            VpcId=vpc_id 
        )
        security_group_id = security_group_response['GroupId']
        print(f"Security group created: {security_group_id}")
        
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Allow SSM HTTPS communication from any IP
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Optional: Allow SSH access from any IP
                }
            ]
        )
        print('Inbound rules added for SSM and SSH.')
        return security_group_id
    except botocore.exceptions.ClientError as e:
        print(f"Error as {e}")


def pull_creds():
    with open('../secrets.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            creds = {'access_key': row['Access key ID'],
                     'secret_access_key': row['Secret access key']}

    return creds

def resource_existence(ec2_client):
    resources = ['Vpc','RouteTable','Subnet', 'InternetGateway', 'KeyPair', 'SecurityGroup','Ec2']
    existence = dict.fromkeys(resources, None)
    
    response = ec2_client.describe_vpcs(
        Filters=[
            {'Name': 'tag:Name', 'Values':['Orca']}
        ]
    )
    
    vpcs = response.get('Vpcs', [])
    if vpcs:
        existence['Vpc'] = vpcs[0]['VpcId']
        vpc_filter = {'Name': 'vpc-id', 'Values': [existence['Vpc']]}

        response = ec2_client.describe_route_tables(Filters = [vpc_filter])
        route_tables = response.get('RouteTables', [])
        if route_tables:
            existence['RouteTable'] = route_tables[0]['RouteTableId']
        
        response = ec2_client.describe_subnets(Filters=[vpc_filter])
        subnets = response.get('Subnets', [])
        if subnets:
            existence['Subnet']= subnets[0]['SubnetId']
         
        response = ec2_client.describe_internet_gateways(
            Filters=[
                {'Name': 'attachment.vpc-id', 'Values': [existence['Vpc']]}
            ]
        )
        internet_gateways = response.get('InternetGateways', [])

        if internet_gateways:
            existence['InternetGateway'] = internet_gateways[0]['InternetGatewayId']
        
    response = ec2_client.describe_key_pairs(
        Filters = [{'Name': 'key-name', 'Values': ['orca-ec2-key']}]
    )
    key_pairs = response.get('KeyPairs', [])
    if key_pairs:
        existence['KeyPair'] = key_pairs[0]['KeyPairId']

    response = ec2_client.describe_security_groups(
        Filters=[vpc_filter]
    )
    security_groups = response.get('SecurityGroups',[])
    if security_groups:
        existence['SecurityGroup'] = security_groups[0]['GroupId']

    response = ec2_client.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': ['orca-runner']}
        ]
    )
    
    return existence
    
if __name__ == '__main__':
    creds = pull_creds()
    print(creds)
    session = session_create(creds['access_key'], creds['secret_access_key'])
    ec2_client = session.client('ec2', region_name='us-east-2')
    ec2_create(session, 'us-east-2')

