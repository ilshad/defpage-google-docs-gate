import json
import logging
from pyramid.settings import asbool
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
from defpage.lib.authentication import authenticated
from defpage.gd.config import system_params
from defpage.gd.source import Source
from defpage.gd.source import SourceTypeException
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

def notfound(req):
    req.response.status = 404
    return {}

def api(func):
    def wrapper(req):
        if not asbool(system_params.api):
            raise HTTPNotFound
        return func(req)
    return wrapper

@authenticated
def manage_collection(req):
    cid = int(req.matchdict["name"])
    collection = meta.get_collection(req.user.userid, cid)
    source = collection["source"]

    if source:
        if source["type"] == "gd":
            return HTTPFound(location="/collection/%s/select_folder" % cid)
        return render_to_response("defpage.gd:templates/gd_forbidden.pt",
                                  {"collection":collection}, request=req)

    elif req.POST.get("continue"):
        if meta.set_source(req.user.userid, cid, False):
            return HTTPFound(location="/collection/%s/select_folder" % cid)
        s = Source(cid, req.user.userid)
        url = s.oauth2_step1_get_url()
        logger.info("Request access: %s" % url)
        return HTTPFound(location=url)

    return render_to_response("defpage.gd:templates/manage_collection.pt",
                              {"collection":collection}, request=req)

@authenticated
def gd_oauth2_callback(req):
    cid = int(req.GET.get("state"))
    code = req.GET.get("code")
    error = req.GET.get("error")

    if cid and code:
        s = Source(cid, req.user.userid)
        s.oauth2_step2_run(code)
        return HTTPFound(location="/collection/%s/select_folder" % cid)

    elif cid and error == "access_denied":
        req.session.flash(u"You declined defpage.com access to your google documents")
        return HTTPFound(location="/collection/%s" % cid)

    elif error:
        req.session.flash(u"Error: %s" % error)
        return HTTPFound(location="/error")

    req.session.flash(u"Missing required parameters")
    return HTTPFound(location="/error")

@authenticated
def select_folder(req):
    cid = int(req.matchdict["name"])
    s = Source(cid, req.user.userid)
    can_change = not s.is_complete()
    if req.POST.get("submit") and can_change:
        folder_id = req.POST.get("folder_id")
        if folder_id:
            s.set_folder(folder_id.split(":")[1])
            req.session.flash(u'You have connected defpage.com to the Google Docs'
                              u' folder <em>"%s"</em>' % req.POST.get("folder_title"))
            return HTTPFound(location="/collection/%s" % cid)
    return {'can_change':can_change}

@authenticated
def folders_json(req):
    s = Source(int(req.matchdict["name"]), req.user.userid)
    return Response(body=json.dumps(s.get_folders()), content_type="application/json")

@api
def api_collection(req):
    s = Source(int(req.matchdict["name"]), system_params.system_user)
    try:
        return s.get_docs()
    except SourceTypeException:
        raise HTTPNotFound

@api
def api_document(req):
    s = Source(int(req.matchdict["name"]), system_params.system_user)
    try:
        content = s.content(req.matchdict["uid"])
    except SourceTypeException:
        raise HTTPNotFound
    print content
    return {}
