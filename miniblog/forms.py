from wtforms import Form, TextField, TextAreaField, validators, SelectField
from wtforms.fields.simple import SubmitField


class EntryForm(Form):
    title = TextField('Title:', [validators.Required()])
    text = TextAreaField('Content:', [validators.Required()])
    category = SelectField('Category:')
    submit = SubmitField('Save')
    preview = SubmitField('Preview')


class CategoryForm(Form):
    name = TextField('Name:', [validators.Required()])
    submit = SubmitField('Save')
