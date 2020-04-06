from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
import os
import flask_whooshalchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SECRET_KEY'] = "3755199dcfb07dfa7c007558f0f591db"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= True
app.config['WHOOSH_BASE'] = 'path/to/whoosh/base'
app.config['MAX_SEARCH_RESULTS'] = 50

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login' #This enables a user to login before he can access account
login_manager.login_message_category = 'info'
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "quantrixp@gmail.com"
app.config['MAIL_PASSWORD'] = "quantrix2020"

db = SQLAlchemy(app)
   
from quandromy.users import users
from quandromy.posts import posts
from quandromy.main import main
from quandromy.api.routes import api

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
app.register_blueprint(api)

migrate = Migrate(app, db)
