
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from database import Job, Application, db

application_bp = Blueprint('application', __name__)

@application_bp.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        cover_letter = request.form['cover_letter']
        return render_template('compare.html', job_id=job_id, cover_letter=cover_letter)
    
    return render_template('apply_job.html', job=job)

@application_bp.route('/submit', methods=['POST'])
@login_required
def submit_application():
    data = request.get_json()
    job_id = data['job_id']
    cover_letter = data['cover_letter']
    
    # Create application record
    application = Application(
        job_id=job_id,
        worker_id=current_user.id,
        cover_letter=cover_letter
    )
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'success': True}), 200