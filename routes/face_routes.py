from flask import Blueprint, request, jsonify
import face_recognition

face_bp = Blueprint('face', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@face_bp.route('/verify', methods=['POST'])
def verify_face():
    aadhar_path = request.form['aadhar_path']
    selfie_path = request.form['selfie_path']

    # Load images
    try:
        aadhar_image = face_recognition.load_image_file(aadhar_path)
        selfie_image = face_recognition.load_image_file(selfie_path)
    except Exception as e:
        return jsonify({'verified': False, 'error': f'Error loading images: {str(e)}'})

    # Compare faces
    try:
        aadhar_encoding = face_recognition.face_encodings(aadhar_image)[0]
        selfie_encoding = face_recognition.face_encodings(selfie_image)[0]
        match = face_recognition.compare_faces([aadhar_encoding], selfie_encoding)[0]
    except Exception as e:
        return jsonify({'verified': False, 'error': f'Error during face comparison: {str(e)}'})

    return jsonify({'verified': match})