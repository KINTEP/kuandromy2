from flask import Flask, render_template, url_for, redirect, flash, request
#from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = "3755199dcfb07dfa7c007558f0f591db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #This enables a user to login before he can access account
login_manager.login_message_category = 'info'

class RegistrationForm(FlaskForm):
	username = StringField("Username", validators = [DataRequired(), Length(min = 2, max = 30)])
	#fullname = StringField("Full Name", validators = [DataRequired()])
	email = StringField("Email", validators = [DataRequired(), Email()])
	#describe_company = StringField("Describe your company", validators = [DataRequired(), Length(max = 100)])
	#describe_product = StringField("Describe your products", validators = [DataRequired(), Length(max = 100)])
	password = PasswordField("Password", validators = [DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators = [DataRequired(), EqualTo("password")])
	submit = SubmitField("Join Now")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("The username already exist. Please choose another one")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("The email already exist. Please choose another one")


class LoginForm(FlaskForm):
	#fullname = StringField("Full Name", validators = [DataRequired()])
	email = StringField("Email", validators = [DataRequired(), Email()])
	password = PasswordField("Password", validators = [DataRequired()])
	submit = SubmitField("Log In")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#Creating the database
class User(db.Model, UserMixin):
    """docstring for ."""
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    #fullname = db.Column(db.String(100), nullable = False, default = "Newton")
    #describe_company = db.Column(db.String(100), nullable = False, default = "Kintep")
    #describe_product = db.Column(db.String(200), nullable = False, default = "None")
    password = db.Column(db.String(60), nullable = False)
    #country = db.Column(db.String(200), nullable = False)
    image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    Products = db.relationship('Products', backref = 'producer', lazy = True)

    def __repr__(self):
        return f'''
                 User Name: {self.username} \n
                 Email: {self.email} \n
                 '''

class Products(db.Model):
    """docstring forProducts."""
    id = db.Column(db.Integer, primary_key = True)
    date_uploaded = db.Column(db.DateTime, nullable = False, default = datetime.utcnow())
    product_name = db.Column(db.String(50), nullable = False, default = "No product")
    #product_type = db.Column(db.String(20), nullable = False, default = "None")
    product_description = db.Column(db.Text, nullable = False, default = 'None')
    #product_image = db.Column(db.String(20), nullable = False, default = 'dafault.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f'''Product Name: {self.product_name} \n
                 Product Description: {self.product_description} \n
                 Product Immage: {self.product_image} \n
                 '''

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hash_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account is created', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form = form)

@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next) if next_page else redirect(url_for('account'))
        else:
            flash("Login unsuccessful, please try again", 'danger')
    return render_template("login.html", form = form)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account')
@login_required
def account():
    image_file = url_for('static', filename = 'img/' + current_user.image_file)
    return render_template('account.html', image_file = image_file)

if __name__ == "__main__":
    app.run(debug=True)
