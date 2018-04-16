from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class UrlSearchForm(FlaskForm):
    url = StringField('News story to search', validators=[DataRequired()])
