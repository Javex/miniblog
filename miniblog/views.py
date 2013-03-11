import json
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, \
    HTTPInternalServerError
from pyramid.security import remember, forget
import requests
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql.expression import desc
import transaction

from miniblog.models import DBSession, Entry, Category
from miniblog.forms import EntryForm, CategoryForm


@view_config(route_name='home', renderer='home.mako')
def home(request):
    all_entries = DBSession.query(Entry).order_by(desc(Entry.entry_time)).all()
    return {'entries': all_entries}


@view_config(route_name='add_entry', renderer='add.mako',
             permission='edit')
def add_entry(request):
    form = EntryForm(request.POST)
    if request.method == 'POST':
        entry = Entry(form.data["title"], form.data["text"])
        if "category" in form.data:
            category = DBSession.query(Category)\
                .filter(Category.name == form.data["category"]).one()
            entry.category = category
        DBSession.add(entry)
        DBSession.flush()
        return HTTPFound(location=request.route_url('view_entry', id_=entry.id))
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

@view_config(route_name='manage_categories', renderer='categories.mako',
             permission='edit')
def categories(request):
    form = CategoryForm(request.POST)
    if request.method == 'POST':
        category = Category(form.data['name'])
        DBSession.add(category)
        return HTTPFound(location=request.route_url('home'))
    return {'form': form}




@view_config(route_name='login')
def login(request):
    verify_url = request.registry.settings['persona_verifier_url']
    try:
        assertion = request.POST['assertion']
    except KeyError:
        raise HTTPBadRequest("No assertion provided, could not log in!")
    data = {'assertion': assertion, 'audience': request.host_url}
    resp = requests.post(verify_url, data=data, verify=True)

    if resp.ok:
        verification_data = json.loads(resp.content)

        if verification_data['email'] != request.registry.settings['admin_email']:
            raise HTTPBadRequest("Only the defined administrator is allowed to log in!")

        if verification_data['status'] == 'okay':
            # Log the user in
            headers = remember(request, verification_data['email'])
            return Response(json.dumps(verification_data), headers=headers)

    raise HTTPInternalServerError("Something went wrong with the assertion!")



@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return Response(headers=headers)
