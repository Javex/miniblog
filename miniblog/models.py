from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.schema import ForeignKey
from pyramid.security import Allow, Everyone

from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def userfinder(id_, request):
    if id_ == request.registry.settings['admin_email']:
        return ["administrator"]
    return None


class Entry(Base):
    __tablename__ = 'entry'
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, nullable=False)
    _text = Column('text', Text, nullable=False)
    entry_time = Column(DateTime, nullable=False)
    category_name = Column(Text, ForeignKey('category.name'))
    category = relationship('Category', backref='entries')

    def __init__(self, title, text, category_id=None):
        self.title = title
        self.text = text
        self.category_id = category_id
        self.entry_time = datetime.now()

    @property
    def text(self):
        import markdown
        from markupsafe import escape
        return markdown.markdown(escape(self._text))

    @text.setter
    def text(self, text):
        self._text = text


class Category(Base):
    __tablename__ = 'category'
    name = Column(Text, primary_key=True)

    def __init__(self, name):
        self.name = name


class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'administrator', 'edit') ]
    def __init__(self, request):
        pass
