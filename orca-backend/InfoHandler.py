import boto3
import botocore.exceptions
import csv


class InfoHandler():
    def __init__(self,session):
        self.s3_client = session.client("s3")

    def list_projects(self):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            if 'Contents' in response:
                    print("Objects in the bucket:")
                    for object in response['Contents']:
                        print(object["Key"])
        except botocore.exceptions.ClientError as e:
            print(f"Error listing projects: {e}")

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
    
    runner = ProjectHandler(session, "orca-s3-1738617758188", "test", False)
    

