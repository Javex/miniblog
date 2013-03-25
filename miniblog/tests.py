from miniblog.models import DBSession
from pyramid import testing
import transaction
import unittest




"""class TestMyView(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            MyModel,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = MyModel(name='one', value=55)
            DBSession.add(model)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_it(self):
        from .views import my_view
        request = testing.DummyRequest()
        info = my_view(request)
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'miniblog')"""

class TestForms(unittest.TestCase):

    def test_entry_fdorm(self):
        from miniblog.forms import EntryForm
        from webob.multidict import MultiDict
        from wtforms import TextField, TextAreaField, SelectField, SubmitField
        text = """
        This is a title
        ===============

        This is **bold**.
        """
        form_data = MultiDict({'title': 'My Title', 'text': text})
        form = EntryForm(form_data)
        self.assertEqual(form.title.data, "My Title")
        self.assertEqual(form.text.data, text)
        self.assertEqual(form.category.data, u'None')
        self.assertIsNone(form.category.choices)
        self.assertIsInstance(form.title, TextField)
        self.assertIsInstance(form.text, TextAreaField)
        self.assertIsInstance(form.category, SelectField)
        self.assertIsInstance(form.submit, SubmitField)
        self.assertIsInstance(form.preview, SubmitField)

    def test_category_form(self):
        from miniblog.forms import CategoryForm
        from webob.multidict import MultiDict
        from wtforms import TextField, SubmitField
        form_data = MultiDict({'name': 'My Category'})
        form = CategoryForm(form_data)
        self.assertEqual(form.name.data, 'My Category')
        self.assertIsInstance(form.name, TextField)
        self.assertIsInstance(form.submit, SubmitField)

class TestModels(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        from sqlalchemy import create_engine
        engine = create_engine('sqlite://')
        from miniblog.models import Category, Base, DBSession, cache
        from tempfile import mktemp
        try:
            cache.configure_from_config({'cache.backend': 'dogpile.cache.dbm',
                         'cache.arguments.filename': mktemp()},
                        'cache.')
        except Exception:
            pass
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            for i in range(3):
                category = Category('Category {0}'.format(i))
                DBSession.add(category)

    def tearDown(self):
        DBSession.remove()

    def test_pretty_date(self):
        from datetime import datetime
        from time import time
        from miniblog.models import pretty_date
        # test diff < 0
        now = time()
        before = now + 1
        self.assertRaises(ValueError, pretty_date, before)

        # test just now
        now = time()
        before = now
        self.assertEqual(pretty_date(before), "just now")
        before = now - 9
        self.assertEqual(pretty_date(before), "just now")

        # test x seconds ago
        now = time()
        before = now - 10
        self.assertEqual(pretty_date(before), "10 seconds ago")
        before = now - 59
        self.assertEqual(pretty_date(before), "59 seconds ago")

        # test a minute ago
        now = time()
        before = now - 60
        self.assertEqual(pretty_date(before), "a minute ago")
        before = now - 119
        self.assertEqual(pretty_date(before), "a minute ago")

        # test x minutes ago
        now = time()
        before = now - 120
        self.assertEqual(pretty_date(before), "2 minutes ago")
        before = now - 3599
        self.assertEqual(pretty_date(before), "59 minutes ago")

        # test an hour ago
        now = time()
        before = now - 3600
        self.assertEqual(pretty_date(before), "an hour ago")
        before = now - 7199
        self.assertEqual(pretty_date(before), "an hour ago")

        # test x hours ago
        now = time()
        before = now - 7200
        self.assertEqual(pretty_date(before), "2 hours ago")
        before = now - 86399
        self.assertEqual(pretty_date(before), "23 hours ago")

        # test Yesterday
        now = time()
        before = now - 86400
        self.assertEqual(pretty_date(before), "Yesterday")
        before = now - 172799
        self.assertEqual(pretty_date(before), "Yesterday")

        # test x days ago
        now = datetime.now()
        before = datetime(now.year, now.month, now.day - 2, now.hour,
                          now.minute, now.second)
        self.assertEqual(pretty_date(before), "2 days ago")
        before = datetime(now.year, now.month, now.day - 7, now.hour,
                          now.minute, now.second + 1)
        self.assertEqual(pretty_date(before), "6 days ago")

        # test a week ago
        now = datetime.now()
        before = datetime(now.year, now.month, now.day - 7, now.hour,
                          now.minute, now.second)
        self.assertEqual(pretty_date(before), "a week ago")
        before = datetime(now.year, now.month, now.day - 14, now.hour,
                          now.minute, now.second + 1)
        self.assertEqual(pretty_date(before), "a week ago")

        # test x weeks ago
        now = datetime.now()
        before = datetime(now.year, now.month, now.day - 14, now.hour,
                          now.minute, now.second)
        self.assertEqual(pretty_date(before), "2 weeks ago")
        before = datetime(now.year, now.month - 1, now.day, now.hour,
                          now.minute, now.second + 1)

        # test a month ago
        now = datetime.now()
        before = datetime(now.year, now.month - 1, now.day, now.hour,
                          now.minute, now.second)
        self.assertEqual(pretty_date(before), "a month ago")

        # test x months ago
        now = datetime.now()
        before = datetime(now.year, now.month - 2, now.day, now.hour,
                          now.minute, now.second)
        self.assertEqual(pretty_date(before), "2 months ago")

        # test a year ago
        now = datetime.now()
        before = datetime(now.year - 1, now.month, now.day, now.hour,
                          now.minute, now.second)
        self.assertEqual(pretty_date(before), "a year ago")

        # test x years ago
        now = datetime.now()
        before = datetime(now.year - 2, now.month, now.day, now.hour,
                          now.minute, now.second)
        self.assertEqual(pretty_date(before), "2 years ago")

    def test_get_categories(self):
        from miniblog.models import get_categories
        categories = get_categories()
        self.assertEqual(len(categories), 3)
        for i in range(3):
            self.assertEqual(categories[i].name, "Category {0}".format(i))

    def test_get_recent_posts(self):
        from miniblog.models import get_recent_posts, Entry
        from time import sleep
        # test with not enough entries
        DBSession.add(Entry('Title 1', 'Text 1'))
        self.assertEqual(len(get_recent_posts()), 1)

        # make sure caching is still in place
        # sleep(1)  # activate this when order test fails
        DBSession.add(Entry('Title 2', 'Text 2'))
        self.assertEqual(len(get_recent_posts()), 1)

        # Invalidate and recount
        get_recent_posts.invalidate()
        self.assertEqual(len(get_recent_posts()), 2)

        # Check order is correct
        recent = get_recent_posts()
        first = recent[0].entry_time
        second = recent[1].entry_time
        self.assertGreater(first, second)

        # Check count param:
        self.assertEqual(len(get_recent_posts(1)), 1)

        for i in range(3, 9):
            DBSession.add(Entry('Title {0}'.format(i),
                                'Text {0}'.format(i)))
        get_recent_posts.invalidate()
        self.assertEqual(len(get_recent_posts()), 7)

    def test_userfinder(self):
        from miniblog.models import userfinder
        request = testing.DummyRequest()
        request.registry.settings["admin_email"] = "test@example.com"

        self.assertEqual(userfinder("test@example.com", request),
                         ["administrator"])
        self.assertEqual(userfinder("test@wrong.com", request),
                         None)

    def test_Entry_text(self):
        from miniblog.models import Entry

        # Ensure Markdown is active
        text = ("This is a title \n"
        "========================")
        expected = "<h1>This is a title</h1>"
        entry = Entry('Title...', text)
        self.assertEqual(entry.text, expected)
        self.assertEqual(entry.title, 'Title...')

        # Ensure escape is active
        text = "<p>Test</p>"
        expected = u"<p>&lt;p&gt;Test&lt;/p&gt;</p>"
        entry = Entry('Title', text)
        self.assertEqual(entry.text, expected)

    def test_Entry_trimmed_text(self):
        from miniblog.models import Entry
        text = ("First paragraph\n"
                "\n"
                "Second paragraph\n"
                "\n"
                "Third paragraph\n")
        entry = Entry('Title', text)
        self.assertNotIn("Third paragraph", entry.trimmed_text)

    def test_Entry_pretty_date(self):
        from miniblog.models import Entry

        # just make sure that pretty_date is used at all.
        entry = Entry('', '')
        self.assertEqual(entry.pretty_date, "just now")

    def test_Entry_init(self):
        from miniblog.models import Entry, Category
        from datetime import datetime

        # Ensure that title and text are enforced
        self.assertRaises(TypeError, Entry)
        self.assertRaises(TypeError, Entry, '')
        self.assertRaises(TypeError, Entry, title='')
        self.assertRaises(TypeError, Entry, text='')

        self.assertIsInstance(Entry('', ''), Entry)

        # Now check that category assignment works
        cat = Category('Test')
        DBSession.add(cat)
        entry = Entry('Test Title', 'Text', 'Test')
        DBSession.add(entry)
        DBSession.flush()
        self.assertEqual(entry.category, cat)

        # Test that entry time is set (test on equality would of course fail)
        self.assertLess((datetime.now() - entry.entry_time).seconds, 1)


        # Check title and text are correctly set on arguments
        entry = Entry('Title', 'Text')
        self.assertEqual(entry.title, 'Title')
        self.assertEqual(entry._text, 'Text')

        entry = Entry(title='Title', text='Text')
        self.assertEqual(entry.title, 'Title')
        self.assertEqual(entry._text, 'Text')

    def test_Category_init(self):
        from miniblog.models import Category

        # Test init works
        self.assertEqual(Category('Test').name, 'Test')
        self.assertEqual(Category(name='Test').name, 'Test')
        self.assertRaises(TypeError, Category)
        self.assertRaises(TypeError, Category, 'Test', '...')
        self.assertRaises(TypeError, Category, 'Test', arg='...')

        self.assertEqual(Category('Test').entries, [])

    def test_Category_entries(self):
        from miniblog.models import Category, Entry
        cat = Category('Test')
        entry1 = Entry('Test 1', '...')
        entry2 = Entry('Test 2', '...')

        cat.entries.append(entry1)
        cat.entries.append(entry2)
        DBSession.add(cat)
        DBSession.flush()

        inserted_entry = DBSession.\
            query(Entry).\
            filter(Entry.title == 'Test 1').\
            one()

        self.assertEqual(inserted_entry, entry1)
        self.assertEqual(inserted_entry.category, cat)

    def test_RootFactory(self):
        from miniblog.models import RootFactory
        from pyramid.security import Allow, Everyone
        # simply test for ACL presence
        request = testing.DummyRequest()
        fac = RootFactory(request)
        acl = [ (Allow, Everyone, 'view'),
                (Allow, 'administrator', 'edit') ]
        self.assertEqual(fac.__acl__, acl)

# TODO: Session tests
