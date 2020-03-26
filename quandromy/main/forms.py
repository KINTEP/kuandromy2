from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, FileAllowed
from flask_wtf.file import FileField, FileAllowed

class SearchForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField("Search")

class UploadFileForm(FlaskForm):
    uploadfile = FileField("Upload Profile", validators = [FileAllowed(['jpg', 'png', 'docx', 'mp4', 'jpeg'])])
    submit = SubmitField("Upload")
