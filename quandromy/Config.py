import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = "3755199dcfb07dfa7c007558f0f591db"
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_TRACK_MODIFICATIONS= False
	MAIL_SERVER = 'smtp.googlemail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = "quantrixp@gmail.com"
	MAIL_PASSWORD = "quantrix2020"
	OAUTHLIB_INSECURE_TRANSPORT = True
	GITHUB_OAUTH_CLIENT_SECRET = "b9838bb2c5d4eeffd1acf59347dc5624cd619bb9"
	GITHUB_OAUTH_CLIENT_ID = "0acb3d0b042a3b1dc6fd"
	FACEBOOK_OAUTH_CLIENT_ID = "663729490855447"
	FACEBOOK_OAUTH_CLIENT_SECRET = "aefe081cf32ab312dd3a637b2bac4b83"
	TWITTER_OAUTH_CLIENT_SECRET = "HJQxts9Sy8FPK3v4ej6tlETEcoQyTpowcNEDDF1JuNPucYXdFA"
	TWITTER_OAUTH_CLIENT_KEY = "8Uvg8vvDyEIK4AS5KXvn7hpfj"
	ELASTICSEARCH_URL= 'http://localhost:9200'
	POSTS_PER_PAGE = 5
