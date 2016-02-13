from flask import Flask, render_template, request, flash, session, redirect, url_for, json, jsonify
from werkzeug import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup
import requests
import simplejson

from scraper import *
from models import *

app = Flask(__name__)

app.secret_key = '#'

app.config['SQLALCHEMY_DATABASE_URI'] = '#'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


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
	_user_id = User.query.filter_by(email=session['email']).first().user_id
	history_query = SearchHistory.query.filter_by(user_id=_user_id).order_by(SearchHistory.timestamp.desc()).all()
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
