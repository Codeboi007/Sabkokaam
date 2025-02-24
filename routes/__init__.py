from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
job_bp = Blueprint('job', __name__)
user_bp = Blueprint('user', __name__)
application_bp = Blueprint('application', __name__)

from . import auth_routes, job_routes, user_routes, application_routes