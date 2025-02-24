# routes/application_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db, Application, Job, Users
from flask_login import current_user, login_required
from routes.face_routes import verify_face  # Import the face verification function
from flask import current_app as app
from werkzeug.utils import secure_filename
import os
application_bp = Blueprint('application', __name__, url_prefix='/application')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application_bp.route('/apply_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    if current_user.role != 'worker':
        flash('Only workers can apply for jobs.', 'error')
        return redirect(url_for('user.dashboard'))

    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        cover_letter = request.form['cover_letter']
        if 'face_image' not in request.files:
            flash('No face image part', 'error')
            return redirect(request.url)

        face_image = request.files['face_image']
        if face_image.filename == '':
            flash('No selected face image', 'error')
            return redirect(request.url)

        if face_image and allowed_file(face_image.filename):
            filename = secure_filename(face_image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            face_image.save(image_path)

            # Verify the face
            reference_image_path = current_user.profile_photo
            is_verified = verify_face(image_path, reference_image_path)
            if not is_verified:
                flash('Face verification failed. Please try again with a different image.', 'error')
                return redirect(request.url)

            # Create the application
            new_application = Application(
                job_id=job_id,
                worker_id=current_user.id,
                cover_letter=cover_letter
            )
            db.session.add(new_application)
            db.session.commit()
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('user.view_applications'))
        else:
            flash('Invalid file type. Only images are allowed.', 'error')
            return redirect(request.url)

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
        return redirect(url_for('auth.user_logout'))

    return render_template('view_applications.html', applications=applications)