from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import jwt
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SECRET_KEY = ""

# Database connection
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="",
        password="",
        database="orca"
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
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            token = jwt.encode(
                {
                    'id': user['id'],
                    'email': user['email'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) 
                },
                SECRET_KEY,
                algorithm="HS256"
            )
            return jsonify({"token": token, "user_id": user['id']}), 200 
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    finally:
        cursor.close()
        conn.close()


# Register endpoint
@app.route('/register', methods=['POST'])
def register():
    print("hit")
    data = request.get_json()
    email = data['email']
    password = data['password']
    hashed_password = generate_password_hash(password)

    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
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


if __name__ == '__main__':
    app.run(debug=True)
