from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from flask_login import login_user, logout_user, login_required,current_user
from database import db, Users,UserCategory
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

auth_bp = Blueprint('auth', __name__)

# Registration Route (Handles both GET and POST)
@auth_bp.route('/reg', methods=['GET', 'POST'])
def user_reg():
    if request.method == 'GET':
        # Render the registration page for GET requests
        return render_template('reg.html')

    elif request.method == 'POST':
        try:
            # Extract form data
            full_name = request.form['fullname']
            contact_number = request.form['contact']
            dob=request.form['dob']
            alternate_contact = request.form.get('alternate-contact')  # Use .get() instead of []
            email = request.form['email']
            password = request.form['password']
            aadhar_number = request.form['aadhar']
            country = request.form['country']
            state = request.form['state']
            city = request.form['city']


            # Create user record
            new_user = Users(
                full_name=full_name,
                dob=dob,
                contact_number=contact_number,
                alternate_contact=alternate_contact,
                email=email,
                aadhar_number=aadhar_number,
                is_verified=True,
                country=country,
                state=state,
                city=city
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Flash success message and redirect to login page
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.user_login'))

        except Exception as e:
            logging.error(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('reg.html')

# Login Route
@auth_bp.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect to category selection page if categories are not already selected
            user_categories = UserCategory.query.filter_by(user_id=user.id).all()
            if not user_categories:
                return redirect(url_for('auth.category_selection'))
            
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')

@auth_bp.route('/category-selection', methods=['GET', 'POST'])
@login_required
def category_selection():
    if request.method == 'POST':
        selected_categories = request.form.getlist('category')
        for category in selected_categories:
            user_category = UserCategory(user_id=current_user.id, category=category)
            db.session.add(user_category)
        db.session.commit()
        return redirect(url_for('auth.option_page'))
    return render_template('category.html')

# Logout Route
@auth_bp.route('/logout')
@login_required
def user_logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.user_login'))


@auth_bp.route('/option', methods=['GET'])
def option_page():
    # You can pass dynamic data to the template here if needed
    return render_template('option.html')

