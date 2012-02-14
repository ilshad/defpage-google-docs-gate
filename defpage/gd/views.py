import json
import logging
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.response import Response
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
            s = Source(cid, req.user.userid)
            url = s.oauth2_step1_get_url()
            logger.info("Request access: %s" % url)
            return HTTPFound(location=url)
    return {"collection":collection}

def gd_oauth2_callback(req):
    cid = req.GET.get("state")
    code = req.GET.get("code")
    error = req.GET.get("error")

    if cid and code:
        s = Source(cid, req.user.userid)
        s.oauth2_step2_run(code)
        return HTTPFound(location=s.get_settings_url())

    elif cid and error == "access_denied":
        req.session.flash(u"You declined defpage.com access to your google documents")
        return HTTPFound(location="/collection/%s" % cid)

    elif error:
        req.session.flash(u"Error: %s" % error)
        return HTTPFound(location="/error")

    req.session.flash(u"Missing required parameters")
    return HTTPFound(location="/error")

def select_folder(req):
    s = Source(req.matchdict["name"], req.user.userid)
    can_change = not s.is_complete()
    if req.POST.get("submit") and can_change:
        folder_id = req.POST.get("folder_id")
        if folder_id:
            s.set_folder(folder_id.split(":")[1])
            req.session.flash(u'You have connected DefPage to the Google Docs'
                              u' folder <em>"%s"</em>' % req.POST.get("folder_title"))
            return HTTPFound(location="/group/%s" % req.context.group_id)
    return {'can_change':can_change}

def folders_json(req):
    s = Source(req.matchdict["name"], req.user.userid)
    return Response(body=json.dumps(s.get_folders()), content_type='application/json')
