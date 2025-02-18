import boto3
import botocore.exceptions
import csv
import json

class ProjectHandler():
    def __init__(self, session, bucket_name, project_name, exists):
        self.s3_client = session.client("s3")
        self.bucket_name = bucket_name 
        if not exists:
            self.create_project(project_name)
        self.project_name = project_name
                     
    def create_project(self, project_name):
        # Creates a new folder in s3 where scripts will be stored
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=f"{project_name}/")
            print(f"Created Project {project_name}")
            self.generate_empty_manifest(project_name)
            return project_name

        except botocore.exceptions.ClientError as e:
            print(f"Error creating project folder: {e}")

    
    def generate_empty_manifest(self,project_name):
        manifest_key = f"{project_name}/execution-manifest.json"
        manifest_data = {
            "project": project_name,
            "tasks": []  
        }

        manifest_file = json.dumps(manifest_data, indent=4).encode('utf-8')
        self.s3_client.put_object(Bucket=self.bucket_name, Key=manifest_key, Body=manifest_file)
        print("Empty manifest created.")

    
    def add_file_to_project(file_name, file_content, description=""):
        task_key = f"{self.project_name}/"

        s3_client.put_object(Bucket=bucket_name, Key=task_key, Body=file_content)
        print(f"Task file '{task_key}' uploaded to S3.")

        response = s3_client.get_object(Bucket=bucket_name, Key=manifest_file)
        manifest_data = json.loads(response['Body'].read())

        next_order = len(manifest_data['tasks']) + 1
        new_task = {"key": task_key, "order": next_order, "description": description}
        manifest_data['tasks'].append(new_task)

        updated_manifest = json.dumps(manifest_data, indent=4).encode('utf-8')
        s3_client.put_object(Bucket=bucket_name, Key=manifest_file, Body=updated_manifest)
        print(f"Manifest updated and uploaded to S3 at '{manifest_file}'.")


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
    
    runner = ProjectHandler(session, "orca-s3-1738617758188", "weird", False)
    

