# routes/face_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
import os
from flask import current_app as app
from werkzeug.utils import secure_filename

face_bp = Blueprint('face', __name__)

@face_bp.route('/face_matching', methods=['GET', 'POST'])
@login_required
def face_matching():
    if request.method == 'POST':
        if 'reference_photo' not in request.files:
            flash('No reference photo uploaded', 'error')
            return redirect(request.url)

        reference_photo = request.files['reference_photo']

        if reference_photo.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if reference_photo and allowed_file(reference_photo.filename):
            reference_filename = secure_filename(reference_photo.filename)
            reference_path = os.path.join(app.config['UPLOAD_FOLDER'], reference_filename)
            reference_photo.save(reference_path)

            flash('Reference photo uploaded successfully!', 'success')
            return redirect(url_for('face.face_matching'))

    return render_template('face_matching.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}