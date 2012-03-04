import json
import httplib2
from pyramid.httpexceptions import HTTPUnauthorized
from defpage.lib.exceptions import ServiceCallError
from defpage.gd.config import system_params

def _call(url, method, body=None, headers={}):
    h = httplib2.Http()
    r, c = h.request(system_params.platform_url + url,
                     method=method,
                     body=body,
                     headers=headers)
    if r.status == 401 or r.status == 403:
        raise HTTPUnauthorized
    return r, c

def update_meta(cid):
    r,c = _call("/process", "POST", json.dumps({"update_meta": cid}))
    if r.status != 204:
        raise ServiceCallError
