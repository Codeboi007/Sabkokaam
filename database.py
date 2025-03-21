from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
import json
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    alternate_contact = db.Column(db.String(15))
    email = db.Column(db.String(120), unique=True, nullable=False)
    aadhar_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False) 
    country = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.full_name})>"



class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    people_needed = db.Column(db.Integer, nullable=False)
    working_hours = db.Column(db.String(100), nullable=False)
    earnings = db.Column(db.String(100), nullable=False)
    job_image = db.Column(db.String(200), nullable=True)
    employer_name = db.Column(db.String(100), nullable=False)
    employer_email = db.Column(db.String(100), nullable=False)
    employer_contact = db.Column(db.String(20), nullable=False)
    job_categories = db.Column(db.Text, nullable=False) 
    address = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, job_name, job_description, people_needed, working_hours, earnings, job_image, employer_name, employer_email, employer_contact, job_categories, address, latitude=None, longitude=None):
        self.job_name = job_name
        self.job_description = job_description
        self.people_needed = people_needed
        self.working_hours = working_hours
        self.earnings = earnings
        self.job_image = job_image
        self.employer_name = employer_name
        self.employer_email = employer_email
        self.employer_contact = employer_contact
        self.job_categories = json.dumps(job_categories) 
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.created_at = datetime.utcnow()

    def serialize(self):
        return {
            'id': self.id,
            'job_name': self.job_name,
            'job_description': self.job_description,
            'people_needed': self.people_needed,
            'working_hours': self.working_hours,
            'earnings': self.earnings,
            'job_image': self.job_image,
            'employer_name': self.employer_name,
            'employer_email': self.employer_email,
            'employer_contact': self.employer_contact,
            'job_categories': json.loads(self.job_categories),  
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at
        }


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected',name="job_status"), default='pending')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "worker_id": self.worker_id,
            "status": self.status,
            "applied_at": self.applied_at
        }


class UserCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<UserCategory {self.category}>'


