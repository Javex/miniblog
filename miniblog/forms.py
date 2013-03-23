from wtforms import Form, TextField, TextAreaField, validators, SelectField
from wtforms.fields.simple import SubmitField


class EntryForm(Form):
    """
    Form for adding an entry.

    Notices that the choices need to be specifically added upon recieving a
    request:

    .. code-block: python

        from miniblog.forms import EntryForm
        form = EntryForm(request.POST)
        form.category.choices = [('', ' - None - ')] # + more categories

    Also for proper HTML5 usage, it is recommended to set the ``required``
    attribute for :attr:`EntryForm.title` and :attr:`EntryForm.text`:

    .. code-block:
        form.title(required=True)
        form.text(required=True)

    This is most likely done in the template (e.g. ``templates/add.mako``).

    Attrs:
        ``title``: Title of the blog post. Required.

        ``text``: Full text. Supports Markdown (see ...)

        .. todo::

            Insert ref to Markdown explanation.

        ``category``: A list of categories, needs to be instantiated newly for
        each request as it is dynamic.

        ``submit``: This button is pressed if a new article should be saved.
        Check for it with ``form.submit.data`` (either ``True`` or ``False``).

        ``preview``: This button is pressend when the article should not be
        saved but instead rendered and shown. See ``submit`` for usage.
    """
    title = TextField('Title:', [validators.Required()])
    text = TextAreaField('Content:', [validators.Required()])
    category = SelectField('Category:')
    submit = SubmitField('Save')
    preview = SubmitField('Preview')


class CategoryForm(Form):
    """Very simple form to add a category. Just enter a name and hit 'Save'.

    Attrs:
        ``name``: The name of the category.

        ``submit``: Button that is pressed to save new category.
    """
    name = TextField('Name:', [validators.Required()])
    submit = SubmitField('Save')
