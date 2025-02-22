# app.py
from flask import Flask,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,current_user
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from database import db
from routes import auth_bp, job_bp, user_bp, application_bp
from elasticsearch import Elasticsearch
es = Elasticsearch(hosts=["http://localhost:9200"]) 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.user_login'

with app.app_context():
    db.drop_all()
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    from database import Users
    return Users.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    else:
        return redirect(url_for('auth.user_reg'))
    
# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(job_bp, url_prefix='/job')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(application_bp, url_prefix='/application')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)