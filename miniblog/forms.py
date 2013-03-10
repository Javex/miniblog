from wtforms import Form, TextField, TextAreaField, validators
from wtforms.fields.simple import SubmitField


class EntryForm(Form):
    title = TextField('Title:', [validators.Required()])
    text = TextAreaField('Content:', [validators.Required()])
    submit = SubmitField('Speichern')
