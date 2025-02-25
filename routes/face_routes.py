# routes/face_routes.py
from flask import Blueprint, request, jsonify, current_app as app
from flask_login import current_user
import os
from werkzeug.utils import secure_filename
from database import db, Users
from PIL import Image
import numpy as np

face_bp = Blueprint('face', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@face_bp.route('/upload_reference', methods=['POST'])
def upload_reference():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'{current_user.id}_profile.jpg')
        file.save(filepath)
        current_user.profile_photo = filepath
        db.session.commit()
        return jsonify({'message': 'Profile photo saved'}), 200
    
    return jsonify({'error': 'Invalid file type'}), 400

@face_bp.route('/get_reference/<int:user_id>', methods=['GET'])
def get_reference(user_id):
    user = Users.query.get_or_404(user_id)
    if not os.path.exists(user.profile_photo):
        return jsonify({'error': 'Reference photo not found'}), 404
    
    return jsonify({'url': f'/uploads/{os.path.basename(user.profile_photo)}'}), 200

@face_bp.route('/verify', methods=['POST'])
def verify_face():
    # Ensure a file is uploaded
    if 'file' not in request.files:
        return jsonify({'verified': False, 'error': 'No captured image'}), 400
    
    # Save the captured image
    captured_file = request.files['file']
    captured_path = os.path.join(app.config['UPLOAD_FOLDER'], 'captured.jpg')
    captured_file.save(captured_path)
    
    # Get the user's stored profile photo
    reference_path = current_user.profile_photo
    
    # Check if the reference photo exists
    if not os.path.exists(reference_path):
        return jsonify({'verified': False, 'error': 'Reference photo not found'}), 404
    
    # Load images
    try:
        reference_img = Image.open(reference_path).convert('RGB')
        captured_img = Image.open(captured_path).convert('RGB')
    except Exception as e:
        return jsonify({'verified': False, 'error': f'Error loading images: {str(e)}'}), 500
    
    # Simple pixel comparison (replace with robust logic if needed)
    ref_array = np.array(reference_img)
    cap_array = np.array(captured_img)
    
    # Check if image sizes match
    if ref_array.shape != cap_array.shape:
        return jsonify({'verified': False, 'error': 'Image sizes mismatch'}), 400
    
    # Calculate match percentage
    match = np.sum(ref_array == cap_array) / ref_array.size * 100
    print(f"Match Percentage: {match}%")  # Debug log
    
    # Return verification result
    return jsonify({'verified': match > 80}), 200



