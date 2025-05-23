import boto3
import botocore.exceptions
import csv
import time
import json

class AWSResourceManager:
    def __init__(self, session, region_name):
        self.region_name = region_name
        self.ec2_client = session.client('ec2')
        self.ssm_client = session.client('ssm')
        self.s3_client = session.client('s3')
        self.iam_client = session.client('iam')

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

    def create_iam_role(self):
        role_name='OrcaSSMRole'
        try:
            assume_role_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            }

            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(assume_role_policy),
                Description='Role for EC2 instance with SSM access',
                Tags=[{'Key': 'Name', 'Value': 'orca-ec2-role'}]
            )
            print(response)
            print(f"IAM Role Created: {role_name}")
            return role_name
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            print(f"IAM Role Already Exists: {role_name}")
            return role_name
    
    def attach_ssm_policy_to_role(self ):
        role_name='OrcaSSMRole'
        self.iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
        )
        print(f"Attached AmazonSSMManagedInstanceCore to {role_name}")

    def create_instance_profile(self):
        profile_name='OrcaInstanceProfile'
        role_name='OrcaSSMRole'

        try:
            self.iam_client.create_instance_profile(InstanceProfileName=profile_name)
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            pass  # Ignore if already created

        # Attach the role to the instance profile
        profile = self.iam_client.get_instance_profile(InstanceProfileName=profile_name)
        attached_roles = [r['RoleName'] for r in profile['InstanceProfile']['Roles']]

        if role_name not in attached_roles:
            self.iam_client.add_role_to_instance_profile(
                InstanceProfileName=profile_name,
                RoleName=role_name
            )
            print(f"Attached role '{role_name}' to instance profile '{profile_name}'")
        else:
            print(f"Role '{role_name}' already attached to instance profile '{profile_name}'")

        print(f"Instance Profile '{profile_name}' with Role '{role_name}' is ready")



        return profile_name

    def attach_s3_access_policy_to_role(self, bucket_name):
        role_name = 'OrcaSSMRole'
        s3_rw_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ]
            }
        ]
        }

        self.iam_client.put_role_policy(
        RoleName=role_name,
        PolicyName='OrcaS3ReadWriteAccess',
        PolicyDocument=json.dumps(s3_rw_policy)
    )

    def create_ec2_instance(self, existing_resources):
        self.create_iam_role()
        self.attach_ssm_policy_to_role()
        self.attach_s3_access_policy_to_role(existing_resources["S3"])
        self.create_instance_profile()
        time.sleep(10)
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
                    IamInstanceProfile={'Name': 'OrcaInstanceProfile'},
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

    def check_attached_policies(self):
        try:
            user_name = self.get_user_name()
            if not user_name:
                print("Unable to retrieve user name.")
                return []

            response = self.iam_client.list_attached_user_policies(UserName=user_name)
            attached_policies = [policy['PolicyArn'] for policy in response.get('AttachedPolicies', [])]
            print("Attached Policies:", attached_policies)
            return attached_policies
        except botocore.exceptions.ClientError as e:
            print(f"Error checking attached policies: {e}")
            return []

    def get_policy_permissions(self, policy_arn):
        try:
            policy_version = self.iam_client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
            policy_document = self.iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)
            
            statements = policy_document['PolicyVersion']['Document']['Statement']
            allowed_actions = []

            if isinstance(statements, dict): 
                statements = [statements]

            for statement in statements:
                if statement['Effect'] == 'Allow':
                    if isinstance(statement['Action'], list):
                        allowed_actions.extend(statement['Action'])
                    else:
                        allowed_actions.append(statement['Action'])

            return allowed_actions
        except botocore.exceptions.ClientError as e:
            print(f"Error fetching policy details: {e}")
            return []

    def check_required_policies(self):
        required_actions = [ "ec2:DescribeInstances","ec2:CreateVpc","ec2:ModifyVpcAttribute","ec2:DescribeVpcs","ec2:CreateSubnet","ec2:DescribeSubnets","ec2:ModifySubnetAttribute","ec2:CreateInternetGateway","ec2:DescribeInternetGateways","ec2:AttachInternetGateway","ec2:CreateRouteTable","ec2:DescribeRouteTables","ec2:CreateRoute","ec2:AssociateRouteTable","ec2:DescribeAvailabilityZones","ec2:CreateTags","ec2:CreateKeyPair","ec2:CreateSecurityGroup","ec2:DeleteSecurityGroup","ec2:DescribeSecurityGroups","ec2:AuthorizeSecurityGroupIngress","ec2:RunInstances","ec2:TerminateInstances","ec2:StartInstances","ec2:StopInstances","ec2:DescribeInstanceStatus","ec2:DescribeImages","ec2:DescribeKeyPairs","ec2:AllocateAddress","ec2:AssociateAddress","ssm:GetParameter","ssm:SendCommand","ssm:GetCommandInvocation","ssm:DescribeInstanceInformation","ssm:ListCommandInvocations","s3:ListAllMyBuckets","s3:CreateBucket","s3:PutObject","s3:ListBucket","s3:GetObject","s3:DeleteObject","iam:CreateRole","iam:AttachRolePolicy","iam:CreateInstanceProfile","iam:AddRoleToInstanceProfile","iam:GetRole","iam:GetInstanceProfile","iam:ListRoles","iam:GetUser","iam:ListInstanceProfiles","iam:ListAttachedUserPolicies","iam:GetPolicy","iam:GetPolicyVersion","iam:TagRole","iam:PutRolePolicy","iam:PassRole" ]

        attached_policies = self.check_attached_policies()
        user_permissions = set()

        if len(attached_policies) > 1:
            print("Error: Only one policy expected")
            return
        else:
            policy_arn = attached_policies[0]
            user_permissions.update(self.get_policy_permissions(policy_arn))

        missing_permissions = [action for action in required_actions if action not in user_permissions]

        if missing_permissions:
            print("Missing Required Permissions:", missing_permissions)
        else:
            print("All required permissions are granted.")


        return missing_permissions

    def get_user_name(self):
        try:
            response = self.iam_client.get_user()
            return response['User']['UserName']
        except botocore.exceptions.ClientError as e:
            print(f"Error fetching user name: {e}")
            return None




