from wtforms import Form, TextField, TextAreaField, validators, SelectField
from wtforms.fields.simple import SubmitField
from miniblog.models import DBSession, Category


class EntryForm(Form):
    title = TextField('Title:', [validators.Required()])
    text = TextAreaField('Content:', [validators.Required()])
    category = SelectField('Category:',
                           choices=([('', ' - None - ')] + [(name, name)
                                    for name, in DBSession.
                                    query(Category.name)]))
    submit = SubmitField('Speichern')

class CategoryForm(Form):
    name = TextField('Name:', [validators.Required()])
    submit = SubmitField('Speichern')
