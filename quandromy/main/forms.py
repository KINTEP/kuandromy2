from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from flask import request

class SearchForm(FlaskForm):
    q = StringField(('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
    

class UploadFileForm(FlaskForm):
    uploadfile = FileField("Upload Profile", validators = [FileAllowed(['jpg', 'png', 'docx', 'mp4', 'jpeg'])])
    submit = SubmitField("Upload")
