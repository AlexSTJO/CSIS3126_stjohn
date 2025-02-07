import csv
import boto3
import time
import os
import boto3
import botocore.exceptions
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
    


    
if __name__ == '__main__':
    creds = pull_creds()
    print(creds)
    session = session_create(creds['access_key'], creds['secret_access_key'])
    ec2_client = session.client('ec2', region_name='us-east-2')
    ec2_create(session, 'us-east-2')
