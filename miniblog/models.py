from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.schema import ForeignKey

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entry'
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, nullable=False)
    _text = Column('text', Text, nullable=False)
    entry_time = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey('category.name'))

    def __init__(self, title, text, category_id=None):
        self.title = title
        self.text = text
        self.category_id = category_id
        self.entry_time = datetime.now()

    @property
    def text(self):
        import markdown
        # Todo: escape with MarkupSafe
        return markdown.markdown(self._text)

    @text.setter
    def text(self, text):
        self._text = text


class Category(Base):
    __tablename__ = 'category'
    name = Column(Text, primary_key=True)

