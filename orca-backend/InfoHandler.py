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
    
    runner = InfoHandler(session, "orca-s3-1738617758188")
    print(runner.list_projects())
    

