from flask import Flask, render_template, request, flash, session, redirect, url_for, json, jsonify

from flask.ext.sqlalchemy import SQLAlchemy

from werkzeug import generate_password_hash, check_password_hash

#from scraper import scraper

from bs4 import BeautifulSoup

import requests

import simplejson


def get_top_holdings(etf):

	url = 'https://www.spdrs.com/product/fund.seam?ticker={0}'

	r = requests.get(url.format(etf))

	soup = BeautifulSoup(r.text).find('div', class_='sect fund_top_holdings')

	holdings = soup.find_all('td', class_='label')

	holding_dict = {i: holdings[i].contents[0] for i in range(len(holdings))}

	data = soup.find_all('td', class_='data')

	weight_dict = {i/2 : float(data[i].contents[0].rstrip('%')) for i in range(0, len(data), 2)}

	shares_dict = {(i-1)/2 : int(data[i].contents[0].replace(',','')) for i in range(1, len(data), 2)}

	top_holdings = {'holding' : holding_dict, 'weight' : weight_dict, 'shares' : shares_dict}

	print top_holdings

	return top_holdings


def get_country_weights(etf):

	url = 'https://www.spdrs.com/product/fund.seam?ticker={0}'

	r = requests.get(url.format(etf))

	soup = BeautifulSoup(r.text).find('div', id='FUND_COUNTRY_WEIGHTS')

	if soup is None:
		return None

	names = soup.find_all('td', class_='label')

	values = soup.find_all('td', class_='data')

	country_names = {i: names[i].contents[0] for i in range(len(names))}

	country_data = {i: float(values[i].contents[0].rstrip('%')) for i in range(len(values))}

	country_weights = {'country' : country_names, 'weight' : country_data}

	print country_weights

	return country_weights


def get_sector_weights(etf):

	url = 'https://www.spdrs.com/product/fund.seam?ticker={0}'

	r = requests.get(url.format(etf))

	soup = BeautifulSoup(r.text).find('div', id='SectorsAllocChart')

	chart_xml = soup.find('div', style="display: none").contents[0]

	xml_soup = BeautifulSoup(chart_xml, 'xml')

	names = xml_soup.find_all('label')

	values = xml_soup.find_all('value')

	sector_names = {i: names[i].contents[0] for i in range(len(names))}

	sector_data = {i: float(values[i].contents[0].rstrip('%')) for i in range(len(values))}

	sector_weights = {'sector' : sector_names, 'weight' : sector_data}

	print sector_weights

	return sector_weights

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

class TopHolding(db.Model):
	__tablename__ = 'top_holdings_entry'
	id = db.Column(db.Integer, primary_key = True)
	etf = db.Column(db.String(4))
	holding = db.Column(db.String(80))
	weight = db.Column(db.Float)
	shares = db.Column(db.Integer)
   
	def __init__(self, etf, holding, weight, shares):
		self.etf = etf
		self.holding = holding
		self.weight = weight
		self.shares = shares

class CountryWeight(db.Model):
	__tablename__ = 'country_weights_entry'
	id = db.Column(db.Integer, primary_key = True)
	etf = db.Column(db.String(4))
	country = db.Column(db.String(45))
	weight = db.Column(db.Float)
   
	def __init__(self, etf, country, weight):
		self.etf = etf
		self.country = country
		self.weight = weight

class SectorWeight(db.Model):
	__tablename__ = 'sector_weights_entry'
	id = db.Column(db.Integer, primary_key = True)
	etf = db.Column(db.String(4))
	sector = db.Column(db.String(45))
	weight = db.Column(db.Float)
   
	def __init__(self, etf, sector, weight):
		self.etf = etf
		self.sector = sector
		self.weight = weight

class SearchHistory(db.Model):
	__tablename__ = 'search_history'
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer)
	etf = db.Column(db.String(4))
	timestamp = db.Column(db.TIMESTAMP)
   
	def __init__(self, user_id, etf, timestamp):
		self.user_id = user_id
		self.etf = etf
		self.timestamp = timestamp


@app.route('/')
def main():
	if 'email' in session:
		return redirect(url_for('home'))

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

		if len(_password) < 8:
			return json.dumps({'message':'Password must be at least 8 characters'})

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
		if 'email' in session:
			return redirect(url_for('home'))

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
			session['email'] = existing_user.email
			return json.dumps({'message':'Success!'})
		else:
			return json.dumps({'message':'Invalid credentials'})

	elif request.method == 'GET':
		if 'email' in session:
			return redirect(url_for('home'))

		return render_template('signin.html')


@app.route('/home')
def home():
	if 'email' not in session:
		return redirect(url_for('signup'))

	active_user = User.query.filter_by(email=session['email']).first()

	if active_user:
		return render_template('home.html', full_name=active_user.full_name)
	else:
		return redirect(url_for('signup'))


@app.route('/parse', methods=['POST'])
def parse():
	_etf = request.form['etf'].upper()

	top_holdings = {}
	country_weights = {}
	sector_weights = {}

	if SearchHistory.query.filter_by(etf=_etf).first():

		top_holdings_query = TopHolding.query.filter_by(etf=_etf).order_by(TopHolding.weight.desc()).all()
		country_weights_query = CountryWeight.query.filter_by(etf=_etf).order_by(CountryWeight.weight.desc()).all()
		sector_weights_query = SectorWeight.query.filter_by(etf=_etf).order_by(SectorWeight.weight.desc()).all()

		holding_dict = {i: top_holdings_query[i].holding for i in range(len(top_holdings_query))}
		weight_dict = {i: top_holdings_query[i].weight for i in range(len(top_holdings_query))}
		shares_dict = {i: top_holdings_query[i].shares for i in range(len(top_holdings_query))}
		top_holdings = {'holding' : holding_dict, 'weight' : weight_dict, 'shares' : shares_dict}

		country_names = {i: country_weights_query[i].country for i in range(len(country_weights_query))}
		country_data = {i: country_weights_query[i].weight for i in range(len(country_weights_query))}
		country_weights = {'country' : country_names, 'weight' : country_data}

		sector_names = {i: sector_weights_query[i].sector for i in range(len(sector_weights_query))}
		sector_data = {i: sector_weights_query[i].weight for i in range(len(sector_weights_query))}
		sector_weights = {'sector' : sector_names, 'weight' : sector_data}

	else:

		top_holdings = get_top_holdings(_etf)
		country_weights = get_country_weights(_etf)
		sector_weights = get_sector_weights(_etf)

		if top_holdings:
			for i in range(len(top_holdings['holding'])):
				entry = TopHolding(_etf, top_holdings['holding'][i], top_holdings['weight'][i], top_holdings['shares'][i])
				db.session.add(entry)
				db.session.commit()

		if country_weights:
			for i in range(len(country_weights['country'])):
				entry = CountryWeight(_etf, country_weights['country'][i], country_weights['weight'][i])
				db.session.add(entry)
				db.session.commit()

		if sector_weights:
			for i in range(len(sector_weights['sector'])):
				entry = SectorWeight(_etf, sector_weights['sector'][i], sector_weights['weight'][i])
				db.session.add(entry)
				db.session.commit()

	history = SearchHistory(User.query.filter_by(email=session['email']).first().user_id, _etf, None)
	db.session.add(history)
	db.session.commit()

	data = {'top_holdings':top_holdings,
			'country_weights':country_weights,
			'sector_weights':sector_weights}

	return simplejson.dumps(data)

@app.route('/history')
def history():
	if 'email' not in session:
		return redirect(url_for('signin'))

	full_name = User.query.filter_by(email=session['email']).first().full_name

	return render_template('history.html', full_name=full_name)

@app.route('/get_history', methods=['GET'])
def get_history():
	history_query = SearchHistory.query.order_by(SearchHistory.timestamp.desc()).all()
	etf_list = {i: history_query[i].etf for i in range(len(history_query))}
	timestamp = {i: str(history_query[i].timestamp) for i in range(len(history_query))}
	data = {'etf_list':etf_list, 'timestamp':timestamp}

	return simplejson.dumps(data)

@app.route('/signout')
def signout():
	if 'email' not in session:
		return redirect(url_for('signin'))

	session.pop('email', None)
	return redirect('/')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
