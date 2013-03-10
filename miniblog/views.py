from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql.expression import desc

from miniblog.models import DBSession, Entry
from miniblog.forms import EntryForm


@view_config(route_name='home', renderer='home.mako')
def home(request):
    all_entries = DBSession.query(Entry).order_by(desc(Entry.entry_time)).all()
    return {'entries': all_entries}

@view_config(route_name='add_entry', renderer='add.mako')
def add_entry(request):
    form = EntryForm(request.POST)
    if request.method == 'POST':
        entry = Entry(form.data["title"], form.data["text"])
        DBSession.add(entry)
        return HTTPFound(location=request.route_url('home'))
        # add the entry
    return {'form': form}

@view_config(route_name='view_entry', renderer='entry.mako')
def view_entry(request):
    id_ = request.matchdict['id_']
    entry = DBSession.query(Entry).filter(Entry.id == id_).first()
    return {'entry': entry}

@view_config(route_name='about', renderer='about.mako')
def about(request):
    return {}

@view_config(route_name='search', renderer='search.mako')
def search(request):
    results = DBSession.query(Entry).filter(Entry.title.like('%%%s%%' % (request.GET['search']))).all()
    return {'results': results}
