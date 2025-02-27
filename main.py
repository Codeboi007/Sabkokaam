from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from database import db
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.user_routes import user_bp
from routes.application_routes import application_bp
from routes.face_routes import face_bp
from elasticsearch import Elasticsearch
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024 

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.user_login'

es = Elasticsearch(hosts=[os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')])  # Initialize Elasticsearch here

# Load face recognition models (paths should be correctly set)
face_recognition_model_path = "api_models/dlib_face_recognition_resnet_model_v1.dat"
face_landmarks_model_path = "api_models/shape_predictor_68_face_landmarks.dat"
face_encoding_model_path = "api_models/mmod_human_face_detector.dat"

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    from database import Users
    return Users.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('landing.html')

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(job_bp, url_prefix='/job')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(application_bp, url_prefix='/application')
app.register_blueprint(face_bp, url_prefix='/face')

if __name__ == '__main__':
    print("Starting the application...")
    app.run(host='127.0.0.1', port=8000, debug=True)