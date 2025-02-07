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

