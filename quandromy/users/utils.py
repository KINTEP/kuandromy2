import secrets
from flask import url_for, render_template
import os
from PIL import Image
from flask_mail import Message
from quandromy.email import send_email
from quandromy import app

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
	#output_size = (5,5)
	i = Image.open(form_picture)
	#i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn

def save_picture2(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/postpics', picture_fn)
	#output_size = (500,500)
	i = Image.open(form_picture)
	#i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn
"""
def send_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset", sender = "quantrixp@gmail.com", recipients = [user.email])
    msg.body = f'''To reset your password, please visit the link below: {url_for('users.reset_token', token = token, _external = True)}. If you did not make this request, simply ignore this message
    '''
    mail.send(msg)
"""

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(('[Quantrix] Reset Your Password'),
               sender="quantrixp@gmail.com",
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))