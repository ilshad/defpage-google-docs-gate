import logging
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from defpage.lib.authentication import authenticated
from defpage.gd.config import system_params
from defpage.gd.source import Source
from defpage.gd import meta

logger = logging.getLogger("defpage.gd")

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
    if not collection["sources"]:
        if req.POST.get("continue"):
            s = Source(cid)
            url = s.oauth2_step1_get_url()
            logger.info("Request access: %s" % url)
            return HTTPFound(location=url)
    return {"collection":collection}

def gd_oauth2_callback(req):
    cid = req.GET.get("state")
    code = req.GET.get("code")
    error = req.GET.get("error")

    if cid and code:
        s = Source(cid)
        s.oauth2_step2_run(req.user.userid, code)
        return HTTPFound(location=s.get_settings_url())

    elif cid and error == "access_denied":
        req.session.flash(u"You declined defpage.com access to your google documents")
        return HTTPFound(location="/collection/%s" % cid)

    elif error:
        req.session.flash(u"Error: %s" % error)
        return HTTPFound(location="/error")

    req.session.flash(u"Missing required parameters")
    return HTTPFound(location="/error")
