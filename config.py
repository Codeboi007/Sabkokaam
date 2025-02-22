import os
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/ingenious_db'
SECRET_KEY = os.urandom(24)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS