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
        self.manifest_key = f"{project_name}/execution-manifest.json"
        self.objects = self.get_project_objects()

    def create_project(self, project_name):
        # Creates a new folder in s3 where scripts will be stored
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=f"{project_name}/")
            print(f"Created Project {project_name}")
            self.generate_empty_manifest(project_name)
            return project_name

        except botocore.exceptions.ClientError as e:
            print(f"Error creating project folder: {e}")

    def get_project_objects(self):
        try:
            objects = []
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=self.project_name, Delimiter="")
            for obj in response.get("Contents"):
                if obj["Key"] != f"{self.project_name}/":
                    filename = obj["Key"].split("/")[-1] 
                    objects.append(filename)
            return objects
        except botocore.exceptions.ClientError as e:
            return "Error Listing Objects"
    
    def add_object(self, object_name, object_file):
       self.s3_client.put_object(Bucket=self.bucket_name, Key=f"{project_name}/{object_name}", Body=object_file) 
    def delete_object(bucket_name, object_name):
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=f"{self.manifest_key}{object_name}")
            print(f"Deleted {object_key} from {bucket_name}")
        except Exception as e:
            print(f"Error deleting {object_key}: {e}")

    
    def generate_empty_manifest(self,project_name):
        manifest_key = f"{project_name}/execution-manifest.json"
        manifest_data = {
            "Project": project_name,
            "Tasks": [],
        }

        manifest_file = json.dumps(manifest_data, indent=4).encode('utf-8')
        self.s3_client.put_object(Bucket=self.bucket_name, Key=manifest_key, Body=manifest_file)
        print("Empty manifest created.")
    
    def read_manifest(self):
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.manifest_key)
        manifest_content = response["Body"].read().decode("utf-8")
        manifest_data = json.loads(manifest_content)
        return manifest_data
   
    
    def validate_and_submit_manifest(self, manifest_data):
        expected_order = list(range(0, len(manifest_data["Tasks"])))
        order_values = []
        for task in manifest_data["Tasks"]:
            print(task)
            if not task["Name"]:
                return "Unnamed task"
            order_values.append(task["Order"])

        if order_values == expected_order:
            manifest_file = json.dumps(manifest_data, indent=4).encode('utf-8')
            self.s3_client.put_object(Bucket=self.bucket_name, Key=self.manifest_key, Body=manifest_file)
            return "Validated and Submitted"
        else:
            return "Invalid Order"
    
                
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
    
    task_info = {
        "Name": "task3",
        "Order": 2,
        "Inputs": [],
        "Outputs": [],
        "Description": "Test Task 3"
    }

    runner = ProjectHandler(session, "orca-s3-1738617758188", "weird", True)
    manifest_data = runner.read_manifest()
    #print(runner.validate_and_submit_manifest(manifest_data))

