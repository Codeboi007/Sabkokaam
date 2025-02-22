# routes/application_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db, Application, Job, Users
from flask_login import current_user, login_required

application_bp = Blueprint('application', __name__)

@application_bp.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    if current_user.role != 'worker':
        flash('Only workers can apply for jobs.', 'error')
        return redirect(url_for('user.dashboard'))

    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        cover_letter = request.form['cover_letter']
        new_application = Application(
            job_id=job_id,
            worker_id=current_user.id,
            cover_letter=cover_letter
        )
        db.session.add(new_application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('user.view_applications'))

    return render_template('apply_job.html', job=job)

@application_bp.route('/view_applications')
@login_required
def view_applications():
    if current_user.role == 'worker':
        applications = Application.query.filter_by(worker_id=current_user.id).all()
    elif current_user.role == 'employer':
        applications = Application.query.join(Job).filter(Job.employer_id == current_user.id).all()
    else:
        flash('Unknown user role.', 'error')
        return redirect(url_for('auth.logout'))

    return render_template('view_applications.html', applications=applications)