
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from database import Application, Job  

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'worker':
        return render_template('worker_dashboard.html', user=current_user)
    elif current_user.role == 'employer':
        return render_template('employer_dashboard.html', user=current_user)
    else:
        flash('Unknown user role.', 'error')
        return redirect(url_for('auth.logout'))

@user_bp.route('/view_applications')
@login_required
def view_applications():
    if current_user.role == 'worker':
        applications = Application.query.filter_by(worker_id=current_user.id).all()
    elif current_user.role == 'employer':
        applications = Application.query.filter_by(job_id=Job.employer_id == current_user.id).all()
    else:
        flash('Unknown user role.', 'error')
        return redirect(url_for('auth.logout'))

    return render_template('view_applications.html', applications=applications)