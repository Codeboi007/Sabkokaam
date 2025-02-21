from flask import Flask, render_template,redirect,request,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,logout_user,login_required,UserMixin,current_user
from werkzeug.security import generate_password_hash,check_password_hash
import os
from sqlalchemy.exc import IntegrityError
import pymysql

#configurations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root@localhost/ingenious_db'
app.secret_key=os.urandom(24)
db=SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.login_view='login'

#database as a class
class Users(db.Model ,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(200),unique=True,nullable=False)
    phone = db.Column(db.String(15), nullable=False, unique=True) 
    password=db.Column(db.String(200),nullable=False)
    role = db.Column(db.Enum('worker', 'employer'), nullable=False)  
    location = db.Column(db.String(100))  

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
 
    def __repr__(self):
        return f"<User {self.name} ({self.role})>"

#create the db
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(reg_id):
    return Users.query.get(int(reg_id))


#home route
@app.route('/')
def main():
    return redirect(url_for('user_reg'))

#reg route

@app.route('/reg', methods=['GET', 'POST'])
def user_reg():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            role = request.form['role']
            location = request.form['location']

            user_ex = Users.query.filter_by(email=email).first()
            if user_ex:
                flash('User account already exists.')
                return redirect(url_for('user_login'))

            new_user = Users(
                name=name,
                email=email,
                phone=phone,
                role=role,
                location=location
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully.')
            return redirect(url_for('user_login'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred while creating your account. Please try again.')
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred: {str(e)}')
    return render_template('reg.html')

   
#login route
@app.route('/login',methods=['GET', 'POST'])
def user_login():
    if request.method=='POST':
        emailr=request.form['email']
        passwordr=request.form['password']
        user=Users.query.filter_by(email=emailr).first()

        if user and user.check_password(passwordr):
            login_user(user)
            flash('log in success')
            return redirect(url_for('user_reg'))
        else:
            flash('invalid email or password')

    
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

