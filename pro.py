import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://your_db_connection_string'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd()

db = SQLAlchemy(app)
photos = UploadSet("photos", IMAGES)
configure_uploads(app, photos)
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/')
def home():
    return "Welcome to the Photo Gallery"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('gallery'))
        else:
            flash('Invalid login')
    return render_template('login.html')

@app.route('/gallery')
@login_required
def gallery():
    user_id = session['user_id']
    user_photos = Photo.query.filter_by(user_id=user_id).all()
    return render_template('gallery.html', user_photos=user_photos)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'photo' in request.files:
        photo = request.files['photo']
        filename = photos.save(photo)
        user_id = session['user_id']
        new_photo = Photo(filename=filename, user_id=user_id)
        db.session.add(new_photo)
        db.session.commit()
    return redirect(url_for('gallery'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
