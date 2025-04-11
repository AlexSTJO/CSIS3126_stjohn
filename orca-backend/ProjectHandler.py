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
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=f"{project_name}/")
            print(f"Created Project {project_name}")
            self.generate_empty_manifest(project_name)
            self.generate_empty_dependencies(project_name)
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
            task_info["Order"] = len(self.manifest_data["Tasks"]) + 1 
            self.manifest_data["Tasks"].append(task_info)
            if self.validate_and_submit_manifest():
                self.s3_client.put_object(Bucket=self.bucket_name, Key=f"{self.project_name}/{object_name}", Body=object_content)
                return "Object Addition Successful"
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
                    return "Deleted Successfully"             
                else:
                    return "Ensure Order was configured again"
            return "Task not found"

        except Exception as e:
            return e

    def change_task_order(self, old_object_order, new_object_order):
        if old_object_order in range(1, len(self.manifest_data["Tasks"])+1) and new_object_order in range(1, len(self.manifest_data["Tasks"])+1):
            if old_object_order < new_object_order:
                for task_index in range(len(self.manifest_data["Tasks"])):
                    if self.manifest_data["Tasks"][task_index]["Order"] == old_object_order:
                        self.manifest_data["Tasks"][task_index]["Order"] = new_object_order
                    elif new_object_order >= self.manifest_data["Tasks"][task_index]["Order"] and self.manifest_data["Tasks"][task_index]["Order"] > old_object_order:
                        self.manifest_data["Tasks"][task_index]["Order"] -= 1
                return self.validate_and_submit_manifest()
            elif old_object_order > new_object_order:
                for task_index in range(len(self.manifest_data["Tasks"])):
                    if self.manifest_data["Tasks"][task_index]["Order"] == old_object_order:
                        self.manifest_data["Tasks"][task_index]["Order"] = new_object_order
                    elif new_object_order <= self.manifest_data["Tasks"][task_index]["Order"] and self.manifest_data["Tasks"][task_index]["Order"] < old_object_order:
                        self.manifest_data["Tasks"][task_index]["Order"] += 1
                return self.validate_and_submit_manifest()
            else:
                return False
        return False
                    
    
    def generate_empty_manifest(self,project_name):
        manifest_key = f"{project_name}/execution-manifest.json"
        manifest_data = {
            "Project": project_name,
            "Tasks": [],
        }

        manifest_file = json.dumps(manifest_data, indent=4).encode('utf-8')
        self.s3_client.put_object(Bucket=self.bucket_name, Key=manifest_key, Body=manifest_file)
        print("Empty manifest created.")

    def generate_empty_dependencies(self,project_name):
        manifest_key = f"{project_name}/dependencies.txt"

        self.s3_client.put_object( Bucket=self.bucket_name,Key=manifest_key,Body=b'')
        print(f" Created empty dependencies.txt at s3://{self.bucket_name}/{manifest_key}")
        
    
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
        if order_values == expected_order:
            manifest_file = json.dumps(self.manifest_data, indent=4).encode('utf-8')
            self.s3_client.put_object(Bucket=self.bucket_name, Key=self.manifest_key, Body=manifest_file)
            return True
        else:
            return False
   
    def update_task_info(self, task_info):
        for task_index in range(len(self.manifest_data["Tasks"])):
            if self.manifest_data["Tasks"][task_index]["Name"] == task_info["Name"]:
                task_info["Order"] = self.manifest_data["Tasks"][task_index]["Order"] 
                self.manifest_data["Tasks"][task_index] = task_info
                if self.validate_and_submit_manifest():
                    return "Updated task info"
                else:
                    return "Invalid Task Info"
        return "Did not find task"
    
    def update_all_task_info(self, tasks):
        self.manifest_data["Tasks"] = tasks
        if self.validate_and_submit_manifest():
            return "Success"
        return "Error"
    
    def get_dependencies(self):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=f"{self.project_name}/dependencies.txt")
            content = response["Body"].read().decode("utf-8")
            dependencies = content.strip().splitlines()
            return dependencies
        except:
            return "An Error Occurred"
    
    def upload_dependencies(self, dependencies_list):
        if isinstance(dependencies_list, str):
            dependencies_list = dependencies_list.strip().splitlines()
             
        content = "\n".join(dep.strip() for dep in dependencies_list if dep.strip())

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"{self.project_name}/dependencies.txt",
                Body=content.encode("utf-8")
            )
            print(f"Uploaded dependencies.txt")
            return True
        except Exception as e:
            print(f"Error uploading dependencies: {e}")
            return False

    
                


    

