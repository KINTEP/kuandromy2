import secrets
from flask import current_app, url_for
import os
from PIL import Image
from flask_mail import Message

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(current_app.root_path, 'static/img', picture_fn)
	#output_size = (5,5)
	i = Image.open(form_picture)
	#i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn

def save_picture2(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(current_app.root_path, 'static/postpics', picture_fn)
	#output_size = (500,500)
	i = Image.open(form_picture)
	#i.thumbnail(output_size)
	i.save(picture_path)
	return picture_fn

def send_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset", sender = "quantrixp@gmail.com", recipients = [user.email])
    msg.body = f'''To reset your password, please visit the link below: {url_for('users.reset_token', token = token, _external = True)}. If you did not make this request, simply ignore this message
    '''
    mail.send(msg)
