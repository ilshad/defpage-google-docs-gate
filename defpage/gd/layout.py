from pyramid.renderers import get_renderer
from defpage.gd.config import system_params

def renderer_add_globals(e):
    e["layout"] = get_renderer("defpage.gd:templates/layout.pt").implementation()
    e["base_url"] = system_params.base_url
    e["static_url"] = system_params.static_url
    e["logout_url"] = system_params.logout_url
    e["help_url"] = system_params.help_url

