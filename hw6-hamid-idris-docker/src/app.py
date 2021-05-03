from flask import Flask, render_template, url_for, request, session, redirect, flash, abort
from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from flask_caching import Cache
import os
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'mylogindb'
app.config['MONGO_URI'] ="mongodb://mongodb:27017/mylogindb"

mongo = PyMongo(app)


app.secret_key = 'mysecret'

#file upload config
app.config['UPLOAD_FOLDER'] = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


redis
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://redis:6379/0'})




#main route
@app.route('/')
def index():
    if 'username' in session:
        
        return render_template('layout.html')

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    flash('Invalid username/password combination')
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        flash('That username already exists!')
        return render_template('register.html')

    return render_template('register.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)

    return render_template('index.html')

#file extension split and change to lowercase 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#upload 
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Invalid file extension')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            flash('Image successfuly saved ',)
            return redirect(url_for('display_image', filename=filename))
    if request.method == 'GET':
        return render_template('upload.html')


@app.route('/display/<filename>')
def display_image(filename):

    return redirect(url_for('static', filename='uploads/' + filename), code=301)
  
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
