from flask import Flask, render_template
from flask_login import LoginManager
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from database import db
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.user_routes import user_bp
from routes.application_routes import application_bp
from routes.face_routes import face_bp
from elasticsearch import Elasticsearch
from datetime import timedelta
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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.user_login'

es = Elasticsearch(hosts=[os.getenv('ELASTICSEARCH_HOST')])  



with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    from database import Users
    return Users.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('landing.html')


app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(job_bp, url_prefix='/job')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(application_bp, url_prefix='/application')
app.register_blueprint(face_bp, url_prefix='/face')

if __name__ == '__main__':
    print("Starting the application...")
    app.run(host='127.0.0.1', port=8000, debug=True)