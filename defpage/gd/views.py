from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from defpage.gd.config import system_params

def empty(req):
    return {}

def forbidden(req):
    req.response.status = 403
    return {}

def unauthorized(req):
    req.response.status = 401
    return {}
