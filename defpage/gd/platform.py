import json
import httplib2
from pyramid.httpexceptions import HTTPUnauthorized
from defpage.lib.exceptions import ServiceCallError
from defpage.gd.config import system_params

def _call(url, method, body=None, headers={}):
    h = httplib2.Http()
    r, c = h.request(system_params.platform_url + url, method=method, body=body, headers=headers)
    if r.status == 401 or r.status == 403:
        raise HTTPUnauthorized
    return r, c

def sync_collection_source(cid):
    body = json.dumps({"sync_collection_source":cid})
    print "JSON encoded bpdy: ", body
    r,c = _call("/process", "POST", body)
    if r.status != 204:
        raise ServiceCallError
