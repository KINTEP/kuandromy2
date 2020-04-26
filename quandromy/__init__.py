from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from . Config import Config
from flask import g
from flask_moment import Moment
from elasticsearch import Elasticsearch



bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login' #This enables a user to login before he can access account
login_manager.login_message_category = 'info'
mail = Mail()
moment = Moment()

db = SQLAlchemy()

migrate = Migrate(db)

def create_app(config_class = Config):
	app = Flask(__name__)
	app.config.from_object(Config)
	app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
    if app.config['ELASTICSEARCH_URL'] else None

	with app.app_context():
		db.init_app(app)
		bcrypt.init_app(app)
		login_manager.init_app(app)
		mail.init_app(app)
		migrate.init_app(app)
		moment.init_app(app)
	
	#from quandromy.database import User, Post, Comment, Message, Follow

	from quandromy.users.routes import users
	from quandromy.posts.routes import posts
	from quandromy.main.routes import main
	from quandromy.api.routes import api
	from quandromy.RestApi.posts import RestApi
	from quandromy.github.routes import github_blueprint
	from quandromy.facebook.routes import facebook_blueprint
	from quandromy.twitter.routes import twitter_blueprint

	app.register_blueprint(users)
	app.register_blueprint(posts)
	app.register_blueprint(main)
	app.register_blueprint(api)
	app.register_blueprint(RestApi)
	app.register_blueprint(github_blueprint, url_prefix="/login")
	app.register_blueprint(facebook_blueprint, url_prefix="/login")
	app.register_blueprint(twitter_blueprint, url_prefix="/login")


	return app

