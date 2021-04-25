from flask_wtf import FlaskForm

from wtforms.fields import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired, URL


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description')
    price = DecimalField('Price', validators=[DataRequired()])
    picture_url = StringField('Picture URL')
    submit = SubmitField('Create')
