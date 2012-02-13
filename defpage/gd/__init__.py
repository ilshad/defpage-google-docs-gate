from pyramid.config import Configurator
from pyramid.exceptions import NotFound
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from defpage.lib.authentication import UserInfoAuthenticationPolicy
from defpage.lib.util import is_int
from defpage.gd.config import system_params
from defpage.gd.resources import get_root

def main(global_config, **settings):
    system_params.update(settings)
    session_factory = UnencryptedCookieSessionFactoryConfig("7oDVDSuJ")
    authentication_policy = UserInfoAuthenticationPolicy()
    config = Configurator()
    config.setup_registry(settings=settings,
                          session_factory=session_factory,
                          authentication_policy=authentication_policy,
                          root_factory=get_root)

    config.set_request_property("defpage.gd.security.get_user", "user", reify=True)

    config.add_subscriber("defpage.gd.layout.renderer_add_globals",
                          "pyramid.events.BeforeRender")

    # misc
    config.add_view("defpage.gd.views.forbidden",
                    "", context=Forbidden,
                    renderer="defpage.gd:templates/unauthorized.pt")

    config.add_view("defpage.gd.views.unauthorized",
                    "", context=HTTPUnauthorized,
                    renderer="defpage.gd:templates/unauthorized.pt")
    config.add_view("defpage.gd.views.empty", "",
                    renderer="defpage.gd:templates/notfound.pt",
                    context=NotFound)
    config.add_view("defpage.gd.views.empty",
                    "error",
                    renderer="defpage.gd:templates/error.pt")
    config.add_view("defpage.gd.views.default", "")

    # collection
    config.add_view("defpage.gd.views.create_collection",
                    "create_collection",
                    renderer="defpage.gd:templates/collection/create.pt",
                    permission="create_collection")

    config.add_route("display_collection",
                     "/collection/{name}",
                     custom_predicates=(is_int,))
    config.add_view("defpage.gd.views.display_collection",
                    route_name="display_collection",
                    renderer="defpage.gd:templates/collection/display.pt")

    config.add_route("collection_properties",
                     "/collection/{name}/properties",
                     custom_predicates=(is_int,))
    config.add_view("defpage.gd.views.collection_properties",
                    route_name="collection_properties",
                    renderer="defpage.gd:templates/collection/properties.pt")

    config.add_route("delete_collection",
                     "/collection/{name}/delete",
                     custom_predicates=(is_int,))
    config.add_view("defpage.gd.views.delete_collection",
                    route_name="delete_collection",
                    renderer="defpage.gd:templates/collection/delete.pt")

    config.add_route("collection_roles",
                     "/collection/{name}/roles",
                     custom_predicates=(is_int,))
    config.add_view("defpage.gd.views.collection_roles",
                    route_name="collection_roles",
                    renderer="defpage.gd:templates/collection/roles.pt")

    # source
    config.add_route("source_overview",
                     "/collection/{name}/source",
                     custom_predicates=(is_int,))
    config.add_view("defpage.gd.views.source_overview",
                    route_name="source_overview",
                    renderer="defpage.gd:templates/source/overview.pt")

    # transmission
    config.add_route("transmission_overview",
                     "/collection/{name}/transmission",
                     custom_predicates=(is_int,))
    config.add_view("defpage.gd.views.transmission_overview",
                    route_name="transmission_overview",
                    renderer="defpage.gd:templates/transmission/overview.pt")

    # public collections
    config.add_view("defpage.gd.views.public_overview",
                    "public",
                    renderer="defpage.gd:templates/public/overview.pt")

    return config.make_wsgi_app()
