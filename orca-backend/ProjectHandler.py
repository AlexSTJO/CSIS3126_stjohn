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
        self.manifest_data = self.read_manifest()

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
    
    def add_object(self, object_name, object_content, task_info):
        try:
            if object_name in self.objects:
                return "Object already exists"
            task_info["Order"] = len(self.objects) 
            self.manifest_data["Tasks"].append(task_info)
            if self.validate_and_submit_manifest():
                self.s3_client.put_object(Bucket=self.bucket_name, Key=f"{self.project_name}/{object_name}", Body=object_content)
                return "Object Addition Succesful"
            else:
                return "Error validating"
        except Exception as e:
            return e

    def delete_object(self, object_name):
        try:
            task_to_delete = None
            for task_index in range(len(self.manifest_data["Tasks"])):
                if self.manifest_data["Tasks"][task_index]["Name"] == object_name:
                    task_to_delete = task_index
                elif task_to_delete is not None:
                    self.manifest_data["Tasks"][task_index]["Order"] -= 1
            if task_to_delete is not None:
                self.manifest_data["Tasks"].pop(task_to_delete)
                if self.validate_and_submit_manifest():
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=f"{self.project_name}/{object_name}")
                    return "Deleted Succesfully"             
                else:
                    return "Ensure Order was configured again"
            return "Task not found"

        except Exception as e:
            return e
    
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
   
    
    def validate_and_submit_manifest(self):
        expected_order = list(range(1, len(self.manifest_data["Tasks"])+1))
        order_values = []
        for task in self.manifest_data["Tasks"]:
            if not task["Name"]:
                return "Unnamed task"
            order_values.append(task["Order"])
            print(task)
        if order_values == expected_order:
            manifest_file = json.dumps(self.manifest_data, indent=4).encode('utf-8')
            self.s3_client.put_object(Bucket=self.bucket_name, Key=self.manifest_key, Body=manifest_file)
            return True
        else:
            return False
    
                
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
    object_name = "test2.py"
    task_info = {
        "Name": object_name,
        "Order": None,
        "Inputs": [],
        "Outputs": [],
        "Description": "test2.py"
    }
    with open("test.py", "rb") as file:
        file_content = file.read()

    runner = ProjectHandler(session, "orca-s3-1738617758188", "weird", True)
    
    print(runner.delete_object("test.py"))
    #print(runner.add_object(object_name, file_content, task_info))
    

