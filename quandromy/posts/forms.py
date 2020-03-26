from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators =[DataRequired()])
    describe = TextAreaField('Brief Description', validators = [DataRequired()])
    picture = FileField("Upload Picture", validators = [DataRequired(), FileAllowed(['jpeg', 'png','jpg'])])
    submit = SubmitField("Post")
