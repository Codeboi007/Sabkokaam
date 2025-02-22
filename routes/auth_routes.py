# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import db, Users
from main import app
from config import allowed_file
from flask_login import login_user, current_user, logout_user, login_required
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/reg', methods=['GET', 'POST'])
def user_reg():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            role = request.form['role']
            location = request.form['location']

            if 'profile_photo' not in request.files:
                flash('No file part', 'error')
                return redirect(request.url)

            file = request.files['profile_photo']
            if file.filename == '':
                profile_photo_path = None
            else:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    profile_photo_path = filepath
                else:
                    flash('Invalid file type. Only images are allowed.', 'error')
                    return redirect(request.url)

            user_ex = Users.query.filter_by(email=email).first()
            if user_ex:
                flash('User account already exists.', 'error')
                return redirect(url_for('auth.user_login'))

            new_user = Users(
                name=name,
                email=email,
                phone=phone,
                role=role,
                location=location,
                profile_photo=profile_photo_path
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully.', 'success')
            return redirect(url_for('auth.user_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred: {str(e)}', 'error')
    return render_template('reg.html')

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