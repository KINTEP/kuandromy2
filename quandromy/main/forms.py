from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
    

class UploadFileForm(FlaskForm):
    uploadfile = FileField("Upload Profile", validators = [FileAllowed(['jpg', 'png', 'docx', 'mp4', 'jpeg'])])
    submit = SubmitField("Upload")
