from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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