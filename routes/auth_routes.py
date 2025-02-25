# routes/auth_routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from database import db, Users
from flask import current_app as app
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

auth_bp = Blueprint('auth', __name__)

# Registration Page Route
@auth_bp.route('/reg', methods=['GET'])
def user_reg():
    return render_template('registration.html')  # Render the registration page

# Handle Registration Form Submission
@auth_bp.route('/reg', methods=['POST'])
def user_register():
    try:
        # Extract form data
        full_name = request.form['fullname']
        contact_number = request.form['contact']
        alternate_contact = request.form.get('alternate-contact')
        email = request.form['email']
        password = request.form['password']
        aadhar_number = request.form['aadhar']
        country = request.form['country']
        state = request.form['state']
        city = request.form['city']
        face_verification = request.form['face_verification']

        if face_verification != 'true':
            return jsonify({'success': False, 'error': 'Face verification failed'}), 400

        # Save uploaded files
        aadhar_photo = request.files['aadhar-photo']
        selfie_data = request.form['selfie-data']

        if not aadhar_photo or not selfie_data:
            return jsonify({'success': False, 'error': 'Missing files'}), 400

        aadhar_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(aadhar_photo.filename))
        aadhar_photo.save(aadhar_path)

        # Decode and save selfie photo
        selfie_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{full_name}_selfie.png")
        with open(selfie_path, "wb") as fh:
            fh.write(base64.b64decode(selfie_data.split(',')[1]))

        # Create user record
        new_user = Users(
            full_name=full_name,
            contact_number=contact_number,
            alternate_contact=alternate_contact,
            email=email,
            aadhar_number=aadhar_number,
            aadhar_photo=aadhar_path,
            selfie_photo=selfie_path,
            is_verified=True,
            country=country,
            state=state,
            city=city
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Redirect to login page after successful registration
        return redirect(url_for('auth.user_login'))
    except Exception as e:
        logging.error(f"Error during registration: {e}")
        return jsonify({'success': False, 'error': 'An error occurred during registration'}), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def user_logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.user_login'))