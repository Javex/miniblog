from datetime import datetime
from hashlib import sha512
from pyramid.interfaces import ISession
from pyramid.security import Allow, Everyone
from sqlalchemy import Column, Integer, Text, DateTime, PickleType
from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.schema import ForeignKey
from time import time
from zope.interface import implements
from zope.sqlalchemy import ZopeTransactionExtension
import hmac
import logging
import os


log = logging.getLogger(__name__)
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def detach(db_session):
    """Remove the pyramid session from the database session to prevent errors
    after the transaction has been committed."""
    from pyramid.threadlocal import get_current_request
    request = get_current_request()
    log.debug("Expunging (detaching) session for DBSession")
    db_session.expunge(request.session)


listen(SASession, 'after_commit', detach)
"""Set up listener for after_commit event to detach the pyramid session."""


def userfinder(id_, request):
    """Pass in the email address and only return the administrator principal
    if ``id_`` matches the configuration value ``admin_email``"""
    if id_ == request.registry.settings['admin_email']:
        return ["administrator"]
    return None


class Entry(Base):
    """A single blog entry."""
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
    """A category in the blog."""
    __tablename__ = 'category'
    name = Column(Text, primary_key=True)

    def __init__(self, name):
        self.name = name


class RootFactory(object):
    """A simple factory for the ACL/Authorization system."""
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'administrator', 'edit') ]
    def __init__(self, request):
        pass


class SessionMessage(Base):
    """A message in a specific session with a specific queue. Used for
    pyramids session system."""
    __tablename__ = 'session_message'
    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False)
    queue = Column(Text, default='')
    session_id = Column(Integer, ForeignKey('session.id'))

    def __init__(self, msg, queue=''):
        self.message = msg
        self.queue = queue

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.message

class Session(Base):
    """A session with a specific session ID for a specific client. Used for
    pyramids session system."""
    implements(ISession)

    __tablename__ = 'session'

    id = Column(Text, primary_key=True)
    _created = Column('created', DateTime)
    message_queue = relationship('SessionMessage',
                                 backref='session')
    csrf_token = Column(Text, nullable=False)
    additional_data = Column(PickleType)

    new = False

    def __init__(self, request):
        self.id = os.urandom(20).encode('hex')
        self.request = request
        self._created = datetime.now()
        self.new = True
        self.new_csrf_token()
        self.additional_data = {}

    @property
    def created(self):
        return int(self._created.strftime("%s"))

    @created.setter
    def created(self, time):
        self._created = datetime.fromtimestamp(time)

    def invalidate(self):
        DBSession.delete(self)
        # remove cookie

    def changed(self):
        # Doesn't need to be implemented as SQLAlchemy tracks all mutations
        # in here.
        pass

    def flash(self, msg, queue='', allow_duplicate=True):
        if not allow_duplicate and \
        filter(lambda m: m.queue == queue and
               m.message == msg, self.message_queue):
            return

        message = SessionMessage(msg, queue)
        self.message_queue.append(message)

    def pop_flash(self, queue=''):
        messages = self.peek_flash(queue)
        for message in messages:
            DBSession.delete(message)
        return messages

    def peek_flash(self, queue=''):
        return filter(lambda m: m.queue == queue, self.message_queue)

    def new_csrf_token(self):
        token = os.urandom(20).encode('hex')
        self.csrf_token = token
        return self.csrf_token

    def get_csrf_token(self):
        return self.csrf_token

    def __getitem__(self, key):
        return self.additional_data.__getitem__(key)

    def get(self, key, default=None):
        return self.additional_data.get(key, default)

    def __delitem__(self, key):
        return self.additional_data.__delitem__(key)

    def __setitem__(self, key, value):
        return self.additional_data.__setitem__(key, value)

    def keys(self):
        return self.additional_data.keys()

    def values(self):
        return self.additional_data.values()

    def items(self):
        return self.additional_data.items()

    def iterkeys(self):
        return self.additional_data.iterkeys()

    def itervalues(self):
        return self.additional_data.itervalues()

    def iteritems(self):
        return self.additional_data.iteritems()

    def clear(self):
        return self.additional_data.clear()

    def update(self, d):
        return self.additional_data.update(d)

    def setdefault(self, key, default=None):
        return self.additional_data.setdefault(key, default)

    def pop(self, k, *args):
        return self.additional_data.pop(k, *args)

    def popitem(self):
        return self.additional_data.popitem()

    def __len__(self):
        return self.additional_data.__len__()

    def __iter__(self):
        return self.additional_data.__iter__()

    def __contains__(self, key):
        return self.additional_data.__contains__(key)

    def _set_cookie(self, request, response):
        if not self._cookie_on_exception and \
            getattr(self.request, 'exception', None):
            return False  # don't set a cookie during exceptions
        if len(self._cookie) > 4064:
            raise ValueError("Cookie value is too long to store (%s bytes)"
                             % len(self._cookie))
        if hasattr(response, 'set_cookie'):
            set_cookie = response.set_cookie
        else:
            def set_cookie(*args, **kwargs):
                tmp_response = Response()
                tmp_response.set_cookie(*args, **kwargs)
                response.headerlist.append(tmp_response.headerlist[-1])

        log.debug("Setting cookie %s with value %s for session with id %s" % (self._cookie_name, self._cookie, self.id))
        set_cookie(
            self._cookie_name,
            value=self._cookie,
            max_age=self._cookie_max_age,
            path=self._cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=self._cookie_httponly)


    def configure(self, cookie, on_exception, secure, httponly, path, name,
                  max_age, domain):
        """Store configuration for cookie"""
        self._cookie_on_exception = on_exception
        self._cookie_secure = secure
        self._cookie_httponly = httponly
        self._cookie_path = path
        self._cookie_name = name
        self._cookie_max_age = max_age
        self._cookie_domain = domain
        self._cookie = cookie


def get_session(request):

    on_exception, secure, httponly, path, name, secret, \
        duration, max_age, domain = get_cookie_settings(request)
    try:
        try:
            cookie = request.cookies.get('session').strip('"')
        except AttributeError:
            raise ValueError("No cookie set!")
        hash, session_id, timestamp = cookie.split(":")
        timestamp = int(timestamp)
        log.debug("Data: Cookie: %s, Hash: %s, Session_id: %s, timestamp: %s" % (cookie, hash, session_id, timestamp))
        if hash != calc_digest(secret, session_id, timestamp):
            raise ValueError("Invalid session hash!")
        try:
            session = DBSession.query(Session)\
                .filter(Session.id == session_id).one()
        except NoResultFound:
            raise ValueError("No session found!")

        if timestamp + duration < time():
            DBSession.delete(session)
            raise ValueError("Session expired!")
    except ValueError as e:
        log.debug("The exception message was: %s" % e)
        session, cookie = create_session(secret, request)
        log.debug("Created session with id %s and cookie %s" % (session.id, cookie))
        DBSession.add(session)
    session.configure(cookie, on_exception, secure, httponly, path, name,
                      max_age, domain)
    session.message_queue
    request.add_response_callback(session._set_cookie)
    log.debug("Returning session with id %s for path %s" % (session.id, request.path))
    return session


def create_session(secret, request):
    session = Session(request)
    hash = calc_digest(secret, session.id, session.created)
    cookie = ":".join([hash, session.id, str(session.created)])
    return session, cookie


def calc_digest(secret, session_id, timestamp):
    hash = hmac.new(secret, session_id + str(timestamp), digestmod=sha512)
    return hash.hexdigest()


def get_cookie_settings(request):
    settings = request.registry.settings
    on_exception = settings.get('session.cookie_on_exception', True)
    secure = settings.get('session.cookie_secure', False)
    httponly = settings.get('session.cookie_httponly')
    path = settings.get('session.cookie_path', '/')
    name = settings.get('session.cookie_name', 'session')
    secret = settings.get('session.secret')
    duration = settings.get('session.duration', 3600)
    max_age = settings.get('session.max_age', None)
    domain = settings.get('session.domain', None)
    return on_exception, secure, httponly, path, name, secret, duration, max_age, domain
