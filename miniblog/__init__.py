from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config

from miniblog.models import DBSession, Base, userfinder, get_session, cache


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    cache.configure_from_config(settings, 'dogpile.cache.')
    authn_policy = AuthTktAuthenticationPolicy(settings['auth_secret'],
                                               hashalg='sha512',
                                               callback=userfinder)
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          root_factory='miniblog.models.RootFactory',
                          session_factory=get_session,
                          )
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('home_paged', '/page/{page}')
    config.add_route('add_entry', '/add')
    config.add_route('manage_categories', '/categories')
    config.add_route('delete_category', '/categories/delete/{name_}')
    config.add_route('view_entry', '/entry/{id_}')
    config.add_route('delete_entry', '/entry/{id_}/delete')
    config.add_route('edit_entry', '/entry/{id_}/edit')
    config.add_route('view_categories', '/category/{id_}')
    config.add_route('about', '/about')
    config.add_route('search', '/search')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan()
    return config.make_wsgi_app()
