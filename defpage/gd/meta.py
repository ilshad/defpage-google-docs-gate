import json
import base64
import httplib2
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPUnauthorized
from defpage.lib.exceptions import ServiceCallError
from defpage.gd.config import system_params

def _call(userid, url, method, body=None, headers={}):
    h = httplib2.Http()
    headers.update({"Authorization":"Basic " + base64.b64encode(str(userid or "") + ":1")})
    r, c = h.request(system_params.meta_url + url, method=method, body=body, headers=headers)
    if r.status == 401 or r.status == 403:
        raise HTTPUnauthorized
    return r, c

def get_collection(userid, cid):
    r,c = _call(userid, "/collections/" + str(cid), "GET")
    if r.status == 200:
        return json.loads(c)
    elif r.status == 404:
        raise HTTPNotFound
    raise ServiceCallError

def edit_collection(userid, cid, **kw):
    r,c = _call(userid, "/collections/" + str(cid), "POST", json.dumps(kw))
    if r.status != 204:
        raise ServiceCallError

def set_source(userid, cid, force):
    body = json.dumps({"collection_id":cid, "force":force})
    r,c = _call(userid, "/sources/%s/gd" % str(userid), "POST", body)
    if r.status == 204:
        return True
    elif r.status in (403, 404):
        return False
    raise ServiceCallError

def get_document(docid):
    r,c = _call(userid, "/documents/" + str(docid), "GET")
    if r.status == 200:
        return json.loads(c)
    elif r.status == 404:
        raise HTTPNotFound
    raise ServiceCallError
