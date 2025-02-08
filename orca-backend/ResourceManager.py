import boto3
import botocore.exceptions
import csv
import time

class AWSResourceManager:
    def __init__(self, session, region_name):
        self.region_name = region_name
        self.ec2_client = self.session.client('ec2')
        self.ssm_client = self.session.client('ssm')
        self.s3_client = self.session.client('s3')

    def resource_existence(self):
        resources = ['Vpc', 'RouteTable', 'Subnet', 'InternetGateway', 'KeyPair', 'SecurityGroup', 'Ec2', 'S3']
        existence = dict.fromkeys(resources, None)

        response = self.ec2_client.describe_vpcs(
            Filters=[{'Name': 'tag:Name', 'Values': ['Orca']}]
        )
        vpcs = response.get('Vpcs', [])
        if vpcs:
            existence['Vpc'] = vpcs[0]['VpcId']
            vpc_filter = {'Name': 'vpc-id', 'Values': [existence['Vpc']]}

            response = self.ec2_client.describe_route_tables(Filters=[vpc_filter])
            if response.get('RouteTables'):
                existence['RouteTable'] = response['RouteTables'][0]['RouteTableId']

            response = self.ec2_client.describe_subnets(Filters=[vpc_filter])
            if response.get('Subnets'):
                existence['Subnet'] = response['Subnets'][0]['SubnetId']

            response = self.ec2_client.describe_internet_gateways(
                Filters=[{'Name': 'attachment.vpc-id', 'Values': [existence['Vpc']]}]
            )
            if response.get('InternetGateways'):
                existence['InternetGateway'] = response['InternetGateways'][0]['InternetGatewayId']

        response = self.ec2_client.describe_key_pairs(
            Filters=[{'Name': 'key-name', 'Values': ['orca-ec2-key']}]
        )
        if response.get('KeyPairs'):
            existence['KeyPair'] = response['KeyPairs'][0]['KeyPairId']

        if existence['Vpc']:
            response = self.ec2_client.describe_security_groups(Filters=[vpc_filter])
            if response.get('SecurityGroups'):
                existence['SecurityGroup'] = response['SecurityGroups'][0]['GroupId']

        response = self.ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': ['orca-runner']},
                {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}
            ]
        )
        instances = response.get('Reservations', [])
        if instances:
            existence['Ec2'] = instances[0]['Instances'][0]['InstanceId']
        
        response = self.s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        for bucket in buckets:
            if bucket['Name'].startswith("orca-s3-"):
                existence["S3"] = bucket['Name']                
                    
        return existence

    def create_and_configure_vpc(self, existing_resources):
        try:
            if not existing_resources['Vpc']:
                response = self.ec2_client.create_vpc(
                    CidrBlock='10.0.0.0/24',
                    TagSpecifications=[
                        {'ResourceType': 'vpc', 'Tags': [{'Key': 'Name', 'Value': 'Orca'}]}
                    ]
                )
                existing_resources['Vpc'] = response['Vpc']['VpcId']
                print(f"VPC Created: {existing_resources['Vpc']}")

                self.ec2_client.modify_vpc_attribute(VpcId=existing_resources['Vpc'], EnableDnsSupport={'Value': True})
                self.ec2_client.modify_vpc_attribute(VpcId=existing_resources['Vpc'], EnableDnsHostnames={'Value': True})
            else:
                print(f"VPC Exists: {existing_resources['Vpc']}")

            if not existing_resources['InternetGateway']:
                igw_response = self.ec2_client.create_internet_gateway()
                existing_resources['InternetGateway'] = igw_response['InternetGateway']['InternetGatewayId']
                print(f"Internet Gateway Created: {existing_resources['InternetGateway']}")

                self.ec2_client.attach_internet_gateway(
                    InternetGatewayId=existing_resources['InternetGateway'],
                    VpcId=existing_resources['Vpc']
                )
            else:
                print(f"Internet Gateway Exists: {existing_resources['InternetGateway']}")

            if not existing_resources['Subnet']:
                subnet_response = self.ec2_client.create_subnet(
                    VpcId=existing_resources['Vpc'],
                    CidrBlock='10.0.0.0/26',
                    AvailabilityZone=f"{self.region_name}a"
                )
                existing_resources['Subnet'] = subnet_response['Subnet']['SubnetId']
                print(f"Subnet Created: {existing_resources['Subnet']}")

                self.ec2_client.modify_subnet_attribute(SubnetId=existing_resources['Subnet'], MapPublicIpOnLaunch={'Value': True})
            else:
                print(f"Subnet Exists: {existing_resources['Subnet']}")

            if not existing_resources['RouteTable']:
                route_table_response = self.ec2_client.create_route_table(VpcId=existing_resources['Vpc'])
                existing_resources['RouteTable'] = route_table_response['RouteTable']['RouteTableId']
                print(f"Route Table Created: {existing_resources['RouteTable']}")

                self.ec2_client.create_route(
                    RouteTableId=existing_resources['RouteTable'],
                    DestinationCidrBlock='0.0.0.0/0',
                    GatewayId=existing_resources['InternetGateway']
                )

                self.ec2_client.associate_route_table(SubnetId=existing_resources['Subnet'], RouteTableId=existing_resources['RouteTable'])
                print("Route Table Associated with Subnet")
            else:
                print(f"Route Table Exists: {existing_resources['RouteTable']}")

            return existing_resources

        except botocore.exceptions.ClientError as e:
            print(f"Error: {e}")

    def create_key_pair(self):
        try:
            key_pair_response = self.ec2_client.create_key_pair(KeyName='orca-ec2-key')
            private_key = key_pair_response['KeyMaterial']

            with open('orca-ec2-key.pem', 'w') as key_file:
                key_file.write(private_key)
            print("Key Pair Created and Saved: orca-ec2-key.pem")
        except botocore.exceptions.ClientError as e:
            print(f"Error Creating Key Pair: {e}")

    def create_security_group(self, vpc_id):
        try:
            response = self.ec2_client.create_security_group(
                GroupName='orca-runner-security-group',
                Description='Security group for orca-runner',
                VpcId=vpc_id
            )
            security_group_id = response['GroupId']
            print(f"Security Group Created: {security_group_id}")

            self.ec2_client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {'IpProtocol': 'tcp', 'FromPort': 443, 'ToPort': 443, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                    {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                ]
            )
            print("Inbound Rules Added for SSM and SSH")
            return security_group_id
        except botocore.exceptions.ClientError as e:
            print(f"Error Creating Security Group: {e}")

    def create_ec2_instance(self, existing_resources):
        try:
            if not existing_resources['Ec2']:
                ami_response = self.ssm_client.get_parameter(
                    Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
                )
                ami_id = ami_response['Parameter']['Value']

                response = self.ec2_client.run_instances(
                    ImageId=ami_id,
                    InstanceType='t2.micro',
                    KeyName='orca-ec2-key',
                    SecurityGroupIds=[existing_resources['SecurityGroup']],
                    SubnetId=existing_resources['Subnet'],
                    MinCount=1,
                    MaxCount=1,
                    TagSpecifications=[
                        {'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': 'orca-runner'}]}
                    ]
                )
                instance_id = response['Instances'][0]['InstanceId']
                print(f"EC2 Instance Created: {instance_id}")
                return instance_id
            else:
                print(f"EC2 Instance Exists: {existing_resources['Ec2']}")
        except botocore.exceptions.ClientError as e:
            print(f"Error Creating EC2 Instance: {e}")
    def generate_unique_bucket_name(self):
        unique_suffix = str(int(time.time() * 1000))  
        return f"orca-s3-{unique_suffix}"

    def create_s3_bucket(self):
        max_attempts = 5
        for attempt in range(max_attempts):
            bucket_name = self.generate_unique_bucket_name()
            try:
                response = self.s3_client.create_bucket(
                    Bucket = bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region_name}
                )

                print(f"S3 Bucket Created: {bucket_name}")
                return bucket_name
            except botocore.exceptions.ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'BucketAlreadyExists':
                    print(f"Bucket {bucket_name} already exists. Retrying with a new name...")
                elif error_code == 'BucketAlreadyOwnedByYou':
                    print(f"Bucket {bucket_name} already exists in your account.")
                    return bucket_name, e.response
                else:
                    print(f"Unexpected error: {e}")
                    raise

        raise Exception(f"Failed to create a unique S3 bucket after {max_attempts} attempts.")

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
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name
    )

    resource_manager = AWSResourceManager(session, region_name)

    existing_resources = resource_manager.resource_existence()
    existing_resources = resource_manager.create_and_configure_vpc(existing_resources)

    if not existing_resources['KeyPair']:
        resource_manager.create_key_pair()
    else:
        print(f"Key Pair Exists: {existing_resources['KeyPair']}")

    if not existing_resources['SecurityGroup']:
        existing_resources['SecurityGroup'] = resource_manager.create_security_group(existing_resources['Vpc'])
    else:
        print(f"Security Group Exists: {existing_resources['SecurityGroup']}")
    if not existing_resources['S3']:
        existing_resources["S3"] = resource_manager.create_s3_bucket()
    else:
         print(f"S3 Bucket Exists: {existing_resources['S3']}")
    resource_manager.create_ec2_instance(existing_resources)
