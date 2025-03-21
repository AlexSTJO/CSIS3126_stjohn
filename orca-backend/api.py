from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import jwt
import datetime
from flask_cors import CORS
from CloudHandler import get_db_credentials, get_encryption_key
from Utils import encrypt_secret, decrypt_secret
from dotenv import load_dotenv
import os
import boto3
from ResourceManager import AWSResourceManager
import botocore.exceptions
from InfoHandler import InfoHandler
from ProjectHandler import ProjectHandler
load_dotenv()
app = Flask(__name__)
CORS(app)

SECRET_KEY = get_encryption_key(os.getenv('E_KEY_ID_JWT'))
    
# Database connection
def connect_to_db():
    if os.getenv("DB_HOST") != "localhost":
        creds = get_db_credentials()
    else:
        creds = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASS")
        }
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=creds["user"],
        password=creds["password"],
        database=os.getenv("DB_NAME")
    )

def create_session(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute(
            "SELECT AccessKey, SecretKeyEncrypted, EncryptionKeyId, RegionName FROM cloud_credentials WHERE UserID = %s",
            (user_id,)
        )
    result = cursor.fetchone()
    if result:
        access_key, secret_key_encrypted, encryption_key_id, region_name = result
        encryption_key = get_encryption_key(encryption_key_id)
        secret_key = decrypt_secret(secret_key_encrypted, encryption_key)
        session = boto3.Session(
            aws_access_key_id = access_key,
            aws_secret_access_key = secret_key,
            region_name = region_name
        )
        try:
            session.client('sts').get_caller_identity()
            return session
        except botocore.exceptions.ClientError as e:
            return None
    else:
        return None

    cursor.close()
    conn.close()

def get_cloud_ids(user_id):
    conn = connect_to_db()
    cursor = conn.cursor() 
    cursor.execute(
        "SELECT EC2_ID, S3_ID FROM cloud_info WHERE UserID = %s",
        (user_id,)
    )
    return cursor.fetchone()

        
def retrieve_token_info(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        print('here')
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")
    
# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['PasswordEncrypted'], password):
            token = jwt.encode(
                {
                    'id': user['UserID'],
                    'email': user['Email'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3) 
                },
                SECRET_KEY,
                algorithm="HS256"
            )
            session = create_session(user["UserID"])
            if session:
                link = "true"
            else:
                link = "false"
            return jsonify({"token": token, "link": link}), 200 
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    finally:
        cursor.close()
        conn.close()


# Register endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    hashed_password = generate_password_hash(password)

    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (Email, PasswordEncrypted, EncryptionKeyID) VALUES (%s, %s, %s)", (email, hashed_password, 'none'))
        conn.commit()
        return jsonify({"message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/upload-credentials', methods=['POST'])
def upload_credentials():
    access_key = request.form.get('access_key')
    secret_key = request.form.get('secret_key')
    region_name = request.form.get('region')
    encryption_key_id = os.getenv('E_KEY_ID_CLOUD')
    encryption_key = get_encryption_key(encryption_key_id)


    if not access_key or not secret_key:
        return jsonify({"error": "Missing Credentials or Invalid Token"}), 400
    
    secret_key = encrypt_secret(secret_key, encryption_key) 
    
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 401

    token = token.split(" ")[1] if "Bearer " in token else token

    try:
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id")

        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO cloud_credentials (UserID, AccessKey, SecretKeyEncrypted, EncryptionKeyId, RegionName) VALUES (%s,%s,%s,%s,%s)",
        (user_id, access_key, secret_key, encryption_key_id,region_name,)
        )
        conn.commit()
        session = create_session(user_id)
        if not session:
            cursor.execute(
                "DELETE FROM cloud_credentials WHERE UserID = %s",
                (user_id,)
            )
            conn.commit()
            return jsonify({"error": "Invalid Credentials"}), 401
        else: 
            return jsonify({"message": "Credentials Uploaded"}), 201
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400
    
    finally:
        cursor.close()
        conn.close()

 

@app.route('/credential-reset', methods=['GET'])
def credential_reset():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 401

    token = token.split(" ")[1] if "Bearer " in token else token
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id")
        cursor.execute(
           "DELETE FROM cloud_credentials WHERE UserID = %s",
            (user_id,)
        )
        conn.commit()
        return jsonify({'message': 'Credentials Succesfully Reset'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get-account-info', methods=['GET'])
def get_account_info():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 401

    token = token.split(" ")[1] if "Bearer " in token else token
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id") 
        linked = "False"

        cursor.execute('SELECT Email FROM users WHERE UserID = %s', (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404
        email = result[0]

        cursor.execute('SELECT AccessKey, SecretKeyEncrypted FROM cloud_credentials WHERE UserID = %s', (user_id,))
        result = cursor.fetchone()
        if result:
            linked = "True"
        return jsonify({"Email": email, "Linked": linked})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()

@app.route('/permissions-check', methods=['GET'])
def check_permissions():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 400
    token = token.split(" ")[1] if "Bearer" in token else token
    try:
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id")
        session = create_session(user_id)
        resource_manager = AWSResourceManager(session, session.region_name)
        missing_permissions = resource_manager.check_required_policies()
        if missing_permissions:
            return jsonify({"permissions": {missing_permissions}}), 200
        else:
            return jsonify({"permissions": ""}), 200
    except Exception as e:
        return jsonify({"error": "ensure permissions are added to role"}), 400

@app.route('/check-resource-existence', methods=['GET'])
def check_resource_existence():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 400
    token = token.split(" ")[1] if "Bearer" in token else "token"
    try:
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id")
        session = create_session(user_id)
        resource_manager = AWSResourceManager(session, session.region_name)
        resource_existence = resource_manager.resource_existence()
        if (resource_existence["S3"] and resource_existence["Ec2"]):
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute('SELECT EC2_ID, S3_ID FROM cloud_info WHERE UserID =%s', (user_id,))
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(
                    'INSERT INTO cloud_info (UserID, EC2_ID, S3_ID) VALUES (%s, %s, %s)',
                    (user_id, resource_existence["Ec2"], resource_existence['S3'],)
                )
                conn.commit()
            else:
                existing_ec2, existing_s3 = exists
                if existing_ec2 != resource_existence["Ec2"] or existing_s3 != resource_existence["S3"]:
                    cursor.execute(
                        "UPDATE cloud_info SET EC2_ID = %s, S3_ID = %s WHERE UserID = %s",
                        (resource_existence["Ec2"], resource_existence["S3"], user_id,)
                    )
                    conn.commit()
            cursor.close()
            conn.close()

        
        return jsonify(resource_existence), 200    
    except Exception as e:
        return jsonify({"error": str(e)})    

@app.route('/create-resource', methods=['GET'])
def resource_creation():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 400
    token = token.split(" ")[1] if "Bearer" in token else "token"
    try:
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id")
        session = create_session(user_id)
        resource_manager = AWSResourceManager(session, session.region_name)
        existing_resources = resource_manager.resource_existence()
        existing_resources = resource_manager.create_and_configure_vpc(existing_resources)

        if not existing_resources['KeyPair']:
            resource_manager.create_key_pair()
        else:
            print(f"Key Pair Exists: {existing_resources['KeyPair']}")

        if not existing_resources['SecurityGroup']:
            existing_resources['SecurityGroup'] = resource_manager.create_security_group(existing_resources['Vpc'])
        else:
            print(f"Security Group Exists: {existing_resources['SecurityGroup']}")
        if not existing_resources['S3']:
            existing_resources["S3"] = resource_manager.create_s3_bucket()
        else:
             print(f"S3 Bucket Exists: {existing_resources['S3']}")
        resource_manager.create_ec2_instance(existing_resources)

        return jsonify({'message':'success'}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/list-projects', methods=['GET'])
def list_projects():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 400
    token = token.split(" ")[1] if "Bearer" in token else "token"    
    try:
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id")
        session = create_session(user_id)
        ec2_id, bucket_name = get_cloud_ids(user_id)
        info_handler = InfoHandler(session, bucket_name)
        projects = info_handler.list_projects()
        print(projects)
        return jsonify(projects), 200
    except:
        return({"error": "An Error Occured"}), 400

@app.route('/get-project-tasks/', methods=['GET'])
def get_project_tasks():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 400
    token = token.split(" ")[1] if "Bearer" in token else "token"
    project_name = request.args.get("project")
    if not project_name:
        return jsonify({"error": "Missing project name"}), 400
    try:
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id")
        session = create_session(user_id)
        ec2_id, bucket_name = get_cloud_ids(user_id)
        info_handler = InfoHandler(session, bucket_name)
        projects = info_handler.list_projects()
        if project_name not in projects:
            return jsonify({"error": "An error occurred"}), 400
        project_handler = ProjectHandler(session, bucket_name, project_name , True)
        return jsonify(project_handler.manifest_data["Tasks"]), 200 
    except:
        return({"error": "An Error Occured"}), 400
    
@app.route('/edit-task', methods=['POST'])
def edit_task():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization Token Missing"}), 400
    token = token.split(" ")[1] if "Bearer" in token else "token"
    data = request.get_json()
    project_info = data.get('project_info')
    project_name = project_info["Project"]
    task = data.get('selectedTask')
    if not project_name or not task:
        return jsonify({"error": "Missing project name or task"}), 400
    try:
        decoded_token = retrieve_token_info(token)
        user_id = decoded_token.get("id")
        session = create_session(user_id)
        ec2_id, bucket_name = get_cloud_ids(user_id)
        info_handler = InfoHandler(session, bucket_name)
        projects = info_handler.list_projects() 
        if project_name not in projects:
            return jsonify({"error": "An error occurred"}), 400
        project_handler = ProjectHandler(session, bucket_name, project_name, True)
        if (project_handler.update_task_info(task) =="Invalid Info"):
            return jsonify({"error": "Invalid Info"}), 400
        elif  (project_handler.update_task_info(task) =="Did not find task"):
            return jsonify({"error": "Task Not Found"}), 400

        return jsonify({"message": "Task edited successfully"}), 200
    except:
        return jsonify({"error": "An error occurred"}), 400
if __name__ == '__main__':
    app.run(debug=True)
