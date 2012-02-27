from pyramid.config import Configurator
from pyramid.exceptions import NotFound
from pyramid.exceptions import Forbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from defpage.lib.authentication import UserInfoAuthenticationPolicy
from defpage.lib.util import is_int
from defpage.gd.config import system_params

def main(global_config, **settings):
    system_params.update(settings)
    session_factory = UnencryptedCookieSessionFactoryConfig("Gfj8bTsA")
    authentication_policy = UserInfoAuthenticationPolicy()
    config = Configurator()
    config.setup_registry(settings=settings,
                          session_factory=session_factory,
                          authentication_policy=authentication_policy)

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

    # manage source
    config.add_route("manage_collection", "/collection/{name}",
                     custom_predicates=(is_int,))
    config.add_view("defpage.gd.views.manage_collection",
                    route_name="manage_collection")

    config.add_view("defpage.gd.views.gd_oauth2_callback",
                    "gd_oauth2_callback")

    config.add_route("select_folder", "/collection/{name}/select_folder",
                     custom_predicates=(is_int,))
    config.add_view("defpage.gd.views.select_folder",
                    route_name="select_folder",
                    renderer="defpage.gd:templates/select_folder.pt")

    config.add_route("folders_json", "/collection/{name}/folders_json",
                     custom_predicates=(is_int,))
    config.add_view(route_name="folders_json",
                    view="defpage.gd.views.folders_json")

    # API
    config.add_route("api_collection", "/api/collection/{name}/documents",
                     custom_predicates=(is_int,))
    config.add_view(route_name="api_collection",
                    view="defpage.gd.views.api_collection",
                    renderer="json",
                    request_method="GET")

    return config.make_wsgi_app()
