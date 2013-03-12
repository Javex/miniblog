import json
from pyramid.decorator import reify
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, \
    HTTPInternalServerError
from pyramid.security import remember, forget
import requests
from sqlalchemy import func
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import desc
from sqlalchemy.orm import subqueryload
import transaction
from webob.multidict import MultiDict
import logging

from miniblog.models import DBSession, Entry, Category
from miniblog.forms import EntryForm, CategoryForm

log = logging.getLogger(__name__)

class BaseView(object):

    def __init__(self, request):
        self.request = request

    @reify
    def categories(self):
        categories = DBSession.query(Category)\
            .filter(exists().where(Category.name == Entry.category_name))\
            .all()
        return categories

    @reify
    def recent(self):
        recent_entries = DBSession.query(Entry)\
            .order_by(desc(Entry.entry_time))\
            .all()[:7]
        return recent_entries

    @view_config(route_name='home', renderer='entries.mako')
    @view_config(route_name='home_paged', renderer='entries.mako')
    def home(self):
        page = int(self.request.matchdict.get('num', 1))
        all_entries = DBSession.query(Entry)\
            .order_by(desc(Entry.entry_time))\
            .all()[(page - 1) * 5:page * 5 + 5]
        return {'entries': all_entries}

    @view_config(route_name='view_entry', renderer='entry.mako')
    def view_entry(self):
        id_ = self.request.matchdict['id_']
        entry = DBSession.query(Entry).filter(Entry.id == id_).first()
        return {'entry': entry}

    @view_config(route_name='view_categories', renderer='entries.mako')
    def view_categories(self):
        id_ = self.request.matchdict['id_']
        category = DBSession.query(Category).options(subqueryload(Category.entries)).filter(Category.name == id_).one()
        return {'entries': category.entries}

    @view_config(route_name='about', renderer='about.mako')
    def about(self):
        return {}


    @view_config(route_name='search', renderer='search.mako')
    def search(self):
        results = DBSession.query(Entry)\
            .filter(Entry.title.like('%%%s%%' % (self.request.GET['search'])))\
            .all()
        return {'results': results}

    @view_config(route_name='login')
    def login(self):
        verify_url = self.request.registry.settings['persona_verifier_url']
        try:
            assertion = self.request.POST['assertion']
        except KeyError:
            raise HTTPBadRequest("No assertion provided, could not log in!")
        data = {'assertion': assertion, 'audience': self.request.host_url}
        resp = requests.post(verify_url, data=data, verify=True)

        if resp.ok:
            verification_data = json.loads(resp.content)

            if verification_data['email'] != self.request.registry.settings['admin_email']:
                raise HTTPBadRequest("Only the defined administrator is allowed to log in!")

            if verification_data['status'] == 'okay':
                # Log the user in
                headers = remember(self.request, verification_data['email'])
                return Response(json.dumps(verification_data), headers=headers)

        raise HTTPInternalServerError("Something went wrong with the assertion!")

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        return Response(headers=headers)

class AdminView(BaseView):

    @view_config(route_name='manage_categories', renderer='categories.mako',
                 permission='edit')
    def manage_categories(self):
        form = CategoryForm(self.request.POST)
        if self.request.method == 'POST':
            category = Category(form.data['name'])
            DBSession.add(category)
            return HTTPFound(location=self.request.route_url('manage_categories'))
        categories = DBSession.query(Category).all()
        return {'form': form, 'categories': categories}

    @view_config(route_name='add_entry', renderer='add.mako',
                 permission='edit')
    def add_entry(self):
        form_data = MultiDict(self.request.session.get("add_entry_form", {}))
        form_data.update(self.request.POST)
        form = EntryForm(form_data)
        if self.request.method == 'POST':
            if not form.validate():
                for field, errors in form.errors.items():
                    for error in errors:
                        self.request.session.flash('Field "%s" has the following error: "%s"' % (field, error))
                self.request.session["add_entry_form"] = form.data
                return HTTPFound(location=self.request.route_url('add_entry'))
            entry = Entry(form.data["title"], form.data["text"])
            if "category" in form.data and form.data["category"]:
                category = DBSession.query(Category)\
                    .filter(Category.name == form.data["category"]).one()
                entry.category = category
            del self.request.session["add_entry_form"]
            DBSession.add(entry)
            DBSession.flush()
            return HTTPFound(location=self.request.route_url('view_entry', id_=entry.id))
            # add the entry
        return {'form': form}

    @view_config(route_name='delete_category', permission='edit')
    def delete_category(self):
        category = DBSession.query(Category)\
            .options(subqueryload(Category.entries))\
            .filter(Category.name == self.request.matchdict["name_"])\
            .one()
        if category.entries:
            self.request.session.flash(
                'There are still entries in category %s, cannot delete!'
                % category.name)
        else:
            DBSession.delete(category)
        return HTTPFound(location=self.request.route_url('manage_categories'))

