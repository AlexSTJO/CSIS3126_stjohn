import boto3
import botocore.exceptions
import csv


class InfoHandler():
    def __init__(self, session, bucket_name):
        self.s3_client = session.client("s3", region_name=session.region_name)
        self.bucket_name = bucket_name

    def list_projects(self):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix= "",Delimiter="/")
            projects = [item['Prefix'][:-1] for item in response.get('CommonPrefixes', [])]
            return projects
        except botocore.exceptions.ClientError as e:
            return str(e)
    
    def list_project_items(self, project_name):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=project_name, Delimiter="")
            folder = response.get("Contents")
            for file in folder:
                print(file["Key"])
        except botocore.exceptions.ClientError as e:
            return str(e)

