from flask_wtf import FlaskForm
from wtforms import SubmitField


class FossilsForm(FlaskForm):
    submit = SubmitField('Save fossils')
