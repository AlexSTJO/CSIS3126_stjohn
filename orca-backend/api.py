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
            return jsonify({"token": token, "user_id": user['UserID']}), 200 
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

@app.route('/upload-script', methods=['POST'])
def upload_script():
    user_id = request.form.get('user_id')
    file = request.files['file']

    if not user_id or not file:
        return jsonify({"error": "Missing user ID or file"}), 400

    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO scripts (user_id, file_name) VALUES (%s, %s)",
            (user_id, file.filename)
        )
        conn.commit()
        return jsonify({"message": "Script uploaded successfully!"}), 201
    
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
    encryption_key_id = os.getenv('E_KEY_ID_CLOUD')
    encryption_key = get_encryption_key(encryption_key_id)


    if not user_id or not access_key or not secret_key:
        return jsonify({"error": "Missing Credentials or Invalid Token"}), 400
    
    secret_key = encrypt_secret(secret_key, encryption_key) 
    
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
        "INSERT INTO CloudCredentials (UserID, AccessKey, SecretKeyEncrypted, EncryptionKeyId) VALUES (%s,%s,%s,%s)",
        (user_id, access_key, secret_key, encryption_key_id)
        )
        conn.commit()
        return jsonify({"message": "Credentials Uploaded"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
