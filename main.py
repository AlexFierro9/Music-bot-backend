import datetime
import hashlib

import pymongo
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from pymongo.mongo_client import MongoClient

from response_engine import generate_response, sentiment_finder

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'dummy value 69'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
CORS(app)
uri = "dummy value 53"
client = MongoClient(uri)
db = client["chatbot"]
user_collection = db['auth-data']
user_collection.create_index([("username", pymongo.ASCENDING)], unique=True)
logout_collection = db['expired-tokens']
logout_collection.create_index([("token", pymongo.ASCENDING)], unique=True)


@app.route("/registration", methods=["POST"])
def register():
    new_user = request.get_json()  # store the json body request
    # Creating Hash of password to store in the database
    new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()  # encrypt password
    # Checking if user already exists
    doc = user_collection.find_one({"username": new_user["username"]})  # checking if user exists
    # If not exists than create one
    if not doc:
        # Creating user
        user_collection.insert_one(new_user)
        return jsonify({'msg': 'User created successfully'}), 201
    else:
        return jsonify({'msg': 'Username already exists'}), 409


@app.route("/login", methods=["post"])
def login():
    # Getting the login Details from payload
    login_details = request.get_json()  # store the json body request
    # Checking if user exists in database or not
    user_from_db = user_collection.find_one({'username': login_details['username']})  # search for user in database
    # If user exists
    if user_from_db:
        # Check if password is correct
        encrypted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
        if encrypted_password == user_from_db['password']:
            # Create JWT Access Token
            access_token = create_access_token(identity=user_from_db['username'])  # create jwt token

            # Return Token
            return jsonify(access_token=access_token), 200
    return jsonify({'msg': 'The username or password is incorrect'}), 401


@app.route("/logout", methods=["get"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        jti = hashlib.sha256(jti.encode("utf-8")).hexdigest()
        if logout_collection.find_one({"jti_encoded": f'{jti}'}):
            return jsonify({"msg": "User already logged out"}), 200
        logout_collection.insert_one({"jti_encoded": f"{jti}"})
        return jsonify({"msg": "Successfully logged out"}), 200
    except Exception:
        return jsonify({"msg": "Error processing given request"}), 500


@app.route('/response', methods=["post"])
@jwt_required()
def response():
    jti = get_jwt()["jti"]
    jti = hashlib.sha256(jti.encode("utf-8")).hexdigest()
    if logout_collection.find_one({"jti_encoded": f'{jti}'}):
        return jsonify({"msg": "Resource unavailable, user logged out"}), 401
    try:
        data = request.get_json()
        dialog = data.get('dialog', [])
        user_response = dialog[-1]
        emotion = sentiment_finder(user_response)
        generated_text = generate_response(dialog)
        return jsonify({"msg": "Generation Successful", "mood": emotion, "response": generated_text}), 200
    except Exception:
        return jsonify({"msg": "Error processing your request"}), 500


if __name__ == '__main__':
    app.run()
