from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
	username = StringField("Username", validators = [DataRequired(), Length(min = 2, max = 30)])
	fullname = StringField("Full Name", validators = [DataRequired()])
	email = StringField("Email", validators = [DataRequired(), Email()])
	describe_company = StringField("Describe your company", validators = [DataRequired(), Length(max = 100)])
	describe_product = StringField("Describe your products", validators = [DataRequired(), Length(max = 100)])
	password = PasswordField("Password", validators = [DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators = [DataRequired(), EqualTo("password")])
	submit = SubmitField("Join Now")

class LoginForm(FlaskForm):
	fullname = StringField("Full Name", validators = [DataRequired()])
	email = StringField("Email", validators = [DataRequired(), Email()])
	password = PasswordField("Password", validators = [DataRequired()])
	submit = SubmitField("Log In")
