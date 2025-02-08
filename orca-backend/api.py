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
            "SELECT AccessKey, SecretKeyEncrypted, EncryptionKeyId, RegionName FROM CloudCredentials WHERE UserID = %s",
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
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) 
                },
                SECRET_KEY,
                algorithm="HS256"
            )
            session = create_session(user["UserID"])
            if session:
                link = "true"
            else:
                link = "false"
            return jsonify({"token": token, "user_id": user['UserID'], "link": link}), 200 
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
    user_id = request.form.get('user_id')
    access_key = request.form.get('access_key')
    secret_key = request.form.get('secret_key')
    region_name = request.form.get('region')
    encryption_key_id = os.getenv('E_KEY_ID_CLOUD')
    encryption_key = get_encryption_key(encryption_key_id)


    if not user_id or not access_key or not secret_key:
        return jsonify({"error": "Missing Credentials or Invalid Token"}), 400
    
    secret_key = encrypt_secret(secret_key, encryption_key) 
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
        "INSERT INTO CloudCredentials (UserID, AccessKey, SecretKeyEncrypted, EncryptionKeyId, RegionName) VALUES (%s,%s,%s,%s,%s)",
        (user_id, access_key, secret_key, encryption_key_id,region_name,)
        )
        conn.commit()
        session = create_session(user_id)
        if not session:
            cursor.execute(
                "DELETE FROM CloudCredentials WHERE UserID = %s",
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

 

@app.route('/cloud-resource-creation/<user_id>', methods=['GET'])
def cloud_link(): 
    try:
        session = create_session(user_id)
        if session:
            manager = AWSResourceManager(session, session.region_name)
            existing_resources = manager.resource_existance()
            print(existing_resources)
        else:
            return jsonify({"error": "No credentials found for the given user ID."}), 400
            
    except Exception as e:
        return {"Error": str(e)}
    finally:
        cursor.close()
        conn.close()
@app.route('/credential-reset/<user_id>', methods=['GET'])
def credential_reset(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
           "DELETE FROM CloudCredentials WHERE UserID = %s",
            (user_id,)
        )
        conn.commit()
        return jsonify({'message': 'Credentials Succesfully Reset'}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/get-account-info/<user_id>', methods=['GET'])
def get_account_info(user_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        linked = "False"
        # Query the Users table
        cursor.execute('SELECT Email FROM users WHERE UserID = %s', (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404
        email = result[0]

        # Query the CloudCredentials table
        cursor.execute('SELECT AccessKey, SecretKeyEncrypted FROM CloudCredentials WHERE UserID = %s', (user_id,))
        result = cursor.fetchone()
        if result:
            linked = "True"
        return jsonify({"Email": email, "Linked": linked})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    finally:
        cursor.close()
        conn.close()
if __name__ == '__main__':
    app.run(debug=True)
