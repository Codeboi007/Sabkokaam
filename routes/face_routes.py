# routes/face_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app
from flask_login import current_user, login_required
import os
from werkzeug.utils import secure_filename
import face_recognition

face_bp = Blueprint('face', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def verify_face(image_path, reference_image_path):
    # Load the images
    unknown_image = face_recognition.load_image_file(image_path)
    reference_image = face_recognition.load_image_file(reference_image_path)

    # Get the face encodings
    try:
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        reference_encoding = face_recognition.face_encodings(reference_image)[0]
    except IndexError:
        return False  # No face found in one of the images

    # Compare the faces
    results = face_recognition.compare_faces([reference_encoding], unknown_encoding)
    return results[0]

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