from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    user_metadata = db.Column(JSON, nullable=True)
    blocked = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    app_metadata = db.Column(JSON, nullable=True)
    given_name = db.Column(db.String(150), nullable=True)
    family_name = db.Column(db.String(150), nullable=True)
    name = db.Column(db.String(300), nullable=True)
    nickname = db.Column(db.String(300), nullable=True)
    picture = db.Column(db.String(300), nullable=True)
    user_id = db.Column(db.String(255), nullable=True)
    connection = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    verify_email = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'


with app.app_context():
    db.create_all()

@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.json

    required_fields = ['email', 'password', 'connection']
    
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    
    valid_connections = ["database", "sms"]
    if data['connection'] not in valid_connections:
        return jsonify({"error": "Connection does not support user creation through the API. It must either be a database or SMS connection."}), 400

    
    if 'username' in data and data['connection'] != 'database':  
        return jsonify({"error": "Cannot set username for connection without requires_username."}), 400

    if data['connection'] not in valid_connections:
        return jsonify({"error": "Connection does not exist."}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User already exists"}), 409


    new_user = User(
        email=data['email'],
        phone_number=data.get('phone_number'),
        user_metadata=data.get('user_metadata'),
        blocked=data.get('blocked', False),
        email_verified=data.get('email_verified', False),
        phone_verified=data.get('phone_verified', False),
        app_metadata=data.get('app_metadata'),
        given_name=data.get('given_name'),
        family_name=data.get('family_name'),
        name=data.get('name'),
        nickname=data.get('nickname'),
        picture=data.get('picture'),
        user_id=data.get('user_id'),
        connection=data['connection'],
        password=data['password'],  
        verify_email=data.get('verify_email', True),
        username=data.get('username')
    )

    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User successfully created.",
        "user": {
            "email": new_user.email,
            "phone_number": new_user.phone_number,
            "given_name": new_user.given_name,
            "family_name": new_user.family_name,
            "nickname": new_user.nickname,
            "user_id": new_user.user_id
        }
    }), 201

@app.errorhandler(401)
def unauthorized_error(e):
    return jsonify({"error": "Invalid token or unauthorized access"}), 401

@app.errorhandler(403)
def forbidden_error(e):
    return jsonify({"error": "Insufficient scope or permissions"}), 403

@app.errorhandler(429)
def too_many_requests_error(e):
    return jsonify({"error": "Too many requests. Please try again later."}), 429

if __name__ == '__main__':
    app.run(debug=True)
