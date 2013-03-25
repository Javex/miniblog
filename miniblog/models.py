from datetime import datetime
from dogpile.cache import make_region
from functools import wraps
from hashlib import sha512
from pyramid.interfaces import ISession
from pyramid.security import Allow, Everyone
from sqlalchemy import Column, Integer, Text, DateTime, PickleType
from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.orm import Session as SASession, scoped_session, sessionmaker, \
    relationship
from sqlalchemy.orm.exc import NoResultFound, DetachedInstanceError
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import desc
from time import time
from zope.interface import implements
from zope.sqlalchemy import ZopeTransactionExtension
import hmac
import logging
import os
import re


log = logging.getLogger(__name__)
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
cache = make_region()


def pretty_date(time=None):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if time is None:
        time = datetime.now()
    try:
        time = datetime.fromtimestamp(time)
    except TypeError:
        if not isinstance(time, datetime):
            raise TypeError("Can only handle datetime or Epoch timestamp.")
    diff = now - time
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        raise ValueError("time parameter must be before now(), not after.")

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 14:
        return "a week ago"
    if now.year == time.year:
        if now.month == time.month:
            return "{0} weeks ago".format(day_diff / 7)
        if now.month - time.month == 1:
            return "a month ago"
        else:
            return "{0} months ago".format(now.month - time.month)
    elif now.year - time.year == 1:
        return "a year ago"
    else:
        return "{0} years ago".format(now.year - time.year)


@cache.cache_on_arguments()
def get_categories():
    """Get a list of all categories. Uses caching for quicker results."""
    return DBSession.query(Category.name).all()


@cache.cache_on_arguments()
def get_recent_posts(count=7):
    """Get a list of recent posts. Uses caching for quicker results.

    Args:
        ``count``: Number of recent posts to retrieve. Default: 7

    Returns:
        A list of :class:`Entry` which are the most recent posts."""
    return DBSession.query(Entry)\
        .order_by(desc(Entry.entry_time))[:count]


def userfinder(id_, request):
    """Pass in the email address and only return the administrator principal
    if ``id_`` matches the configuration value ``admin_email``"""
    if id_ == request.registry.settings['admin_email']:
        return ["administrator"]
    return None


class Entry(Base):
    """A single blog entry.

    Attrs:
        ``id``: ID of the entry, used in URLs for instance.

        ``title``: The title of the entry, rendered as ``<h1>``-Tag in
        template.

        ``_text``: The raw markdown text. Use ``Entry.text`` instead.

        ``entry_time``: The the entry was made.

        ``category_name``: Primary key of :class:`Category` and the name of
        the category this article belongs to.

        ``category``: Full access to the associated :class:`Category`.
    """
    __tablename__ = 'entry'
    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, nullable=False)
    _text = Column('text', Text, nullable=False)
    entry_time = Column(DateTime, nullable=False)
    category_name = Column(Text, ForeignKey('category.name'))
    category = relationship('Category', backref='entries')

    def __init__(self, title, text, category_name=None):
        self.title = title
        self.text = text
        self.category_name = category_name
        self.entry_time = datetime.now()

    @property
    def text(self):
        """A markdown rendered html string as the article text.

        The markdown text from the database is first escaped and then parsed
        by markdown. Is a property, thus usage is ``entry.text`` _not_
        ``entry.text()``"""
        import markdown
        from markupsafe import escape
        return markdown.markdown(escape(self._text))

    @text.setter
    def text(self, text):
        self._text = text

    @property
    def trimmed_text(self):
        """Same as ``Entry.text`` but only the first two paragraphs."""
        trimmed_paragraphs = re.findall(r'<p>(.*?)<\/p>', self.text)[:2]
        return "".join(map(lambda p: '<p>%s</p>' % p, trimmed_paragraphs))


    @property
    def pretty_date(self):
        """Return a date string according to the :func:pretty_date function."""
        return pretty_date(self.entry_time)


class Category(Base):
    """A category in the blog.

    Attrs:
        ``name``: The name of the category.
    """
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


def mutated_additional_data(func):
    """A decorator to track mutation and propagate it to the database.

    The decorator is to be used on all functions that change the value of the
    :attr:`Session.additional_data` dict. Functions like ``set`` or ``pop``
    need this decorator to ensure the changes are afterwards propagated
    into the database.

    From an implementation point it just sets the complete dictionary as a
    new value."""
    func_name = func.__name__
    @wraps(func)
    def handle_mutate(session, *args, **kwargs):
        log.debug("Mutating value on function %s with args %s and kwargs %s"
                  % (func_name, unicode(args), unicode(kwargs)))
        ret = func(session, *args, **kwargs)
        session._additional_data = session._cache_additional_data
        return ret
    return handle_mutate


class MutableDict(Mutable, dict):
    """Make a mutable dict for SQLAlchemy's ``PickleType``.

    Usage:

    .. code-block:: python

        class MyModel(Base):
            my_data = Column('additional_data',
                             MutableDict.as_mutable(PickleType))
    """
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __delitem__(self, key):
        log.debug('Session change occurred: Deleting key "%s"'
                  % key)
        dict.__delitem__(self, key)
        self.changed()

    def __setitem__(self, key, value):
        log.debug('Session change occurred: Setting key "%s" to value "%s"'
                  % (key, value))
        dict.__setitem__(self, key, value)
        self.changed()

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, state):
        self.update(self)


class Session(Base):
    """A session object for pyramid sessions.

    Implements the :class:`pyramid.interfaces.ISession` interface. While it
    uses a database to store the session, the session id is stored in the
    cookie. Howevever, under certain conditions the data *might* be accessed
    after the request was processed and then the object may be detached from
    the database session. Thus a caching mechanism is implemented
    that locally keeps the relevant copies. It tries to fetch values from
    the database and if a :exc:`sqlalchemy.orm.exc.DetachedInstanceError`
    occurs, it just returns a default (empty) value.

    Attrs:
        ``id``: The session id, a 20 byte hex string matching the one stored
        on the users end in a cookie, e.g.
        ``298f74562fa2c2abfd158725d6e40fdb88cc6503``.

        ``created``: A unix timestamp of when the cookie was created. The
        database stores a :class:`datetime.datetime` object that can be
        accessed through the internal ``_created`` attribute if needed.

        ``csrf_token``: On creation a CSRF token is automatically created.
        This can be used to prevent CSRF attacks (see `OWASP <https://www.owasp.org/index.php/Cross-Site_Request_Forgery_%28CSRF%29>`_
        for details).

        .. note::
            Make sure this is used where needed as it prevents security
            problems.

        ``additional_data``: Don't access this directy, use the session
        object itself as a dictionary (as specified by the
        :class:`ISession <pyramid.interfaces.ISession>` interface).

        ``message_queue``: A list of flash messages of type
        :class:`SessionMessage`. Use it as per interface definition.

        .. note::
            This does not implement the caching mechanism so lazy loading
            might be a problem. However, since all messages are eagerly
            loaded, it should not be a problem.

        ``new``: Whether this is a new session.

        ``cache_*``: These attributes are cache managed. Don't access them
        directly. Ever.
    """
    implements(ISession)
    __tablename__ = 'session'

    _id = Column('id', Text, primary_key=True)
    _created = Column('created', DateTime, nullable=False)
    _csrf_token = Column('csrf_token', Text, nullable=False)
    _additional_data = Column('additional_data',
                              MutableDict.as_mutable(PickleType))
    message_queue = relationship('SessionMessage',
                                 backref='session',
                                 lazy='joined')

    new = False
    db_names = ['id', 'csrf_token', 'additional_data']
    """List of names that are handled dynamically by a cache"""

    _cache_id = None
    _cache_created = None
    _cache_csrf_token = None
    _cache_additional_data = None

    defaults = {'additional_data': {}, 'id': '', 'csrf_token': ''}
    """Default values for specific attributes to be returned if the session
    is detached."""

    _delete_cookie = False
    """Whether the cookie should be deleted. Only used by :meth:`invalidate`.
    """


    def __init__(self, request):
        self.id = os.urandom(20).encode("hex")
        self.request = request
        self._created = datetime.now()
        self._cache_created = self._created
        self.new = True
        self.new_csrf_token()
        self._additional_data = {}
        self._cache_additional_data = self._additional_data

    def __getattr__(self, name):
        """Handle caching access for some values.
        """
        if name in self.db_names:
            cache_val = getattr(self, '_cache_%s' % name)
            if cache_val is None:
                try:
                    setattr(self, '_cache_%s' % name,
                            getattr(self, '_%s' % name))
                except DetachedInstanceError:
                    return self.defaults[name]
                cache_val = getattr(self, '_cache_%s' % name)
            return cache_val
        else:
            return Base.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """Handle caching access for some values."""
        if name in self.db_names:
            log.debug("Setting %s to %s" % (name, value))
            setattr(self, '_%s' % name, value)
            setattr(self, '_cache_%s' % name, getattr(self, name))
        else:
            return super(Session, self).__setattr__(name, value)

    def new_csrf_token(self):
        """Generate a new csrf token and store it in the database."""
        token = os.urandom(20).encode('hex')
        self.csrf_token = token
        return self.csrf_token

    def get_csrf_token(self):
        """Return the current csrf token."""
        return self.csrf_token

    @property
    def created(self):
        return int(self._cache_created.strftime("%s"))

    def invalidate(self):
        """Invalidate the current session.

        Remove the object from the database and delete the cookie on the
        client side. The actual deletion is done by :meth:`_set_cookie`
        with a request callback. Here, only the ``_delete_cookie`` value
        is set to ``True``."""
        DBSession.delete(self)
        self._delete_cookie = True

    def changed(self):
        """Does not need to be implemented as mutation tracking is automatic."""
        pass

    def flash(self, msg, queue='', allow_duplicate=True):
        """Store a given message in the flash queue.

        Args:
            ``msg``: ``unicode`` string to be stored as the message.

            ``queue``: Optionally a queue name. This may be used to
            implement a different error queue. By default it is empty
            (``''``).

            ``allow_duplicate``: Whether the same message is allowed. If
            set to ``False``, the message will not be added a second time
            if it is already present."""
        if not allow_duplicate and \
        filter(lambda m: m.queue == queue and
               m.message == msg, self.message_queue):
            return
        message = SessionMessage(msg, queue)
        self.message_queue.append(message)

    def pop_flash(self, queue=''):
        """Retrieve a list of messages for a given queue.

        Messages are removed from the database after they were retrieved.

        Args:
            ``queue``: A specific queue from which the messages should be
            fetched. If not specified, the default queue is used."""
        messages = self.peek_flash(queue)
        for message in messages:
            DBSession.delete(message)
        return messages

    def peek_flash(self, queue=''):
        """Same as :meth:`pop_flash` but does not delete elements."""
        return filter(lambda m: m.queue == queue, self.message_queue)


    def __getitem__(self, key):
        return self.additional_data.__getitem__(key)

    def get(self, key, default=None):
        return self.additional_data.get(key, default)

    @mutated_additional_data
    def __delitem__(self, key):
        return self.additional_data.__delitem__(key)

    @mutated_additional_data
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

    @mutated_additional_data
    def clear(self):
        return self.additional_data.clear()


    @mutated_additional_data
    def update(self, d):
        return self.additional_data.update(d)

    @mutated_additional_data
    def setdefault(self, key, default=None):
        return self.additional_data.setdefault(key, default)

    @mutated_additional_data
    def pop(self, k, *args):
        return self.additional_data.pop(k, *args)

    @mutated_additional_data
    def popitem(self):
        return self.additional_data.popitem()

    def __len__(self):
        return self.additional_data.__len__()

    def __iter__(self):
        return self.additional_data.__iter__()

    def __contains__(self, key):
        return self._additional_data.__contains__(key)

    def _set_cookie(self, request, response):
        """A request callback to set (or delete) a cookie.

        On an outgoing request a cookie is either set or deleted.
        Largely inspired by
        :meth:`pyramid.session.UnencryptedCookieSessionFactoryConfig._set_cookie`
        with some added extensions for cookie deletion.
        """
        if not self._delete_cookie:
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

            log.debug("Setting cookie %s with value %s for session with id %s"
                      % (self._cookie_name, self._cookie, self.id))
            set_cookie(
                self._cookie_name,
                value=self._cookie,
                max_age=self._cookie_max_age,
                path=self._cookie_path,
                domain=self._cookie_domain,
                secure=self._cookie_secure,
                httponly=self._cookie_httponly)
        else:
            if hasattr(response, 'unset_cookie'):
                unset = response.unset_cookie
            else:
                def unset(*args, **kwargs):
                    tmp_response = Response()
                    tmp_response.set_cookie(*args, **kwargs)
                    response.headerlist.append(tmp_response.headerlist[-1])
            log.debug("Deleting cookie %s from session id %s"
                      % (self._cookie_name, self.id))
            unset(self._cookie_name)

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


class SessionMessage(Base):
    """A single message from a specific queue and a specific session.

    Attrs:
        ``id``: ID of the message. Only needed as primary key

        ``session_id``: Foreign key of the ``session.id`` column.

        ``message``: String with the message to display to the user.

        ``queue``: The queue to which the message belongs. Default: ``''``
    """
    __tablename__ = 'session_message'

    id = Column('id', Integer, primary_key=True)
    session_id = Column('session_id', Text, ForeignKey('session.id'))
    message = Column('message', Text, nullable=False)
    queue = Column('queue', Text, default='')

    def __init__(self, msg, queue=''):
        self.message = msg
        self.queue = queue

    def __str__(self):
        return unicode(self).encode("utf-8")

    def __unicode__(self):
        return self.message


def get_session(request):
    """Session factory for use in app configuration.

    Usage:

    .. code-block:: python

        from mtc3.models.session import get_session
        config = Configurator(session_factory=get_session)
    """

    on_exception, secure, httponly, path, name, secret, \
        duration, max_age, domain = get_cookie_settings(request)
    try:
        try:
            cookie = request.cookies.get('session').strip('"')
        except AttributeError:
            raise ValueError("No cookie set!")
        hash, session_id, timestamp = cookie.split(":")
        timestamp = int(timestamp)
        if hash != calc_digest(secret, session_id, timestamp):
            raise ValueError("Invalid session hash!")
        try:
            session = DBSession.query(Session)\
                .filter(Session._id == session_id).one()
        except NoResultFound:
            raise ValueError("No session in database!")

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
    request.add_response_callback(session._set_cookie)
    log.debug("Returning session with id %s for path %s" % (session.id, request.path))
    return session


def create_session(secret, request):
    """For a secret and a request create a new session and cookie.

    Args:
        ``secret``: A unicode string with the configured secret.

        ``request``: The current request.

    Returns:
        A tuple (``session``, ``cookie``) where ``session`` is of type
        :class:`Session` and ``cookie`` is the cookie value which should be
        set on the client side cookie."""
    session = Session(request)
    hash_ = calc_digest(secret, session.id, session.created)
    cookie = ":".join([hash_, session.id, str(session.created)])
    return session, cookie


def calc_digest(secret, session_id, timestamp):
    """Calculate a signature in the form of an HMAC for the cookie.

    Args:
        ``secret``: Configured secret for session signature.

        ``session_id``: The id of the user's session.

        ``timestamp``: An int denoting the :class:`Session.created <Session>` value.

    Returns:
        A hex-string with the calculated HMAC hash.
    """
    hash_ = hmac.new(secret, session_id + str(timestamp), digestmod=sha512)
    return hash_.hexdigest()


def get_cookie_settings(request):
    """Retrieve settings from configuration.

    Only mandatory setting: ``session.secret``.
    """
    settings = request.registry.settings
    on_exception = settings.get('session.cookie_on_exception', True)
    secure = settings.get('session.cookie_secure', False)
    httponly = settings.get('session.cookie_httponly', True)
    path = settings.get('session.cookie_path', '/')
    name = settings.get('session.cookie_name', 'session')
    secret = settings['session.secret']
    duration = settings.get('session.duration', 3600)
    max_age = settings.get('session.max_age', None)
    domain = settings.get('session.domain', None)
    return on_exception, secure, httponly, path, name, secret, duration, max_age, domain
