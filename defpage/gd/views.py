from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from defpage.lib.authentication import authenticated
from defpage.gd.config import system_params
from defpage.gd import meta

def empty(req):
    return {}

def forbidden(req):
    req.response.status = 403
    return {}

def unauthorized(req):
    req.response.status = 401
    return {}

@authenticated
def manage_collection(req):
    cid = req.matchdict["name"]
    collection = meta.get_collection(req.user.userid, cid)
    return {"collection":collection}
