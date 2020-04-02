from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from quandromy.database import User

class RegistrationForm(FlaskForm):
    fullname = StringField("Full Name", validators = [DataRequired()])
    username = StringField("Username", validators = [DataRequired(), Length(min = 2, max = 30)])
    email = StringField("Email", validators = [DataRequired(), Email()])
    #country = StringField("Country", validators = [DataRequired()])
    picture = FileField("Update Profile Picture", validators = [FileAllowed(['jpg', 'png'])])
    password = PasswordField("Password", validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators = [DataRequired(), EqualTo("password")])
    submit = SubmitField("Join Now")

    def validate_username(self, username): #This is checking if the username already exist
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("The username already exist. Please choose another one")

    def validate_email(self, email):#This is checking if the email already exist
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("The email already exist. Please choose another one")


class LoginForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField("Log In")

class UpdateAccountForm(FlaskForm):
    picture = FileField("Update Profile Picture", validators = [FileAllowed(['jpg', 'png', 'jpeg'])])
    username = StringField("Username", validators = [DataRequired(), Length(min = 2, max = 30)])
    email = StringField("Email", validators = [DataRequired(), Email()])
    fullname = StringField("Full Name", validators = [DataRequired()])
    #country = StringField("Country", validators = [DataRequired()])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError("The username already exist. Please choose another one")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("The email already exist. Please choose another one")

class RequestResetPassword(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        if self.email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is None:
                raise ValidationError("There is no account with that email. You have to first create an account")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators = [DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")

class CommentForm(FlaskForm):
    comment = StringField("Comment", validators = [DataRequired()])
    submit = SubmitField("Post")

class MessageForm(FlaskForm):
    message = TextAreaField(('Message'), validators=[
        DataRequired(), Length(min=0, max=140)])
    submit = SubmitField(('Submit'))