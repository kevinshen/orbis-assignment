from flask import Flask, render_template, request, flash, session, redirect, url_for, json

from flask.ext.sqlalchemy import SQLAlchemy

from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()

app = Flask(__name__)

app.secret_key = '#'

app.config['SQLALCHEMY_DATABASE_URI'] = '#'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

class User(db.Model):
	__tablename__ = 'app_user'
	user_id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(45))
	password = db.Column(db.String(80))
	full_name = db.Column(db.String(45))
	email = db.Column(db.String(80), unique=True)
   
	def __init__(self, username, password, full_name, email):
		self.username = username
		self.set_password(password)
		self.full_name = full_name.title()
		self.email = email.lower()
     
	def set_password(self, password):
		self.password = generate_password_hash(password)
   
	def check_password(self, password):
		return check_password_hash(self.password, password)

@app.route('/')
def main():
	return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
	if request.method == 'POST':

		_username = request.form['username']
		_password = request.form['password']
		_fullname = request.form['fullname']
		_email = request.form['email'].lower()

		if _username.isalnum() != True:
			return json.dumps({'message':'Username must be alphanumeric'})

		existing_user = User.query.filter_by(email=_email.lower()).first()

		if existing_user is not None:
			return json.dumps({'message':'Email is already taken'})
		else:
			new_user = User(_username, _password, _fullname, _email)
			db.session.add(new_user)
			db.session.commit()

			session['email'] = new_user.email
			return json.dumps({'message':'Success!'})

	elif request.method == 'GET':
		return render_template('signup.html')

@app.route('/signin', methods=['POST', 'GET'])
def signin():
	if request.method == 'POST':

		_login = request.form['login']
		_password = request.form['password']

		if '@' in _login:
			existing_user = User.query.filter_by(email=_login.lower()).first()
		else:
			existing_user = User.query.filter_by(username=_login).first()

		if existing_user:
			session['email'] = new_user.email
			return json.dumps({'message':'Success!'})
		else:
			return json.dumps({'message':'Invalid credentials'})

	elif request.method == 'GET':
		if 'email' not in session:
			return render_template('signin.html')
		else:
			return redirect(url_for('home'))


@app.route('/home')
def home():
	if 'email' not in session:
		return redirect(url_for('signup'))

	active_user = User.query.filter_by(email=session['email']).first()

	if active_user:
		return render_template('home.html')
	else:
		return redirect(url_for('signup'))

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
