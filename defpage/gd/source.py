import urllib
import logging
import time
from datetime import datetime
from gdata.gauth import OAuth2Token
from gdata.docs.client import DocsClient
from gdata.client import RequestError
from defpage.gd.config import system_params
from defpage.gd import meta
from defpage.gd import platform

logger = logging.getLogger("defpage.gd")

GD_SCOPE = "https://docs.google.com/feeds/"
USER_AGENT = ""
GET_FOLDER = "https://docs.google.com/feeds/default/private/full/folder:%s"
FOLDERS_LIST = "/feeds/default/private/full/-/folder"
FOLDER_CONTENT = "/feeds/default/private/full/folder:%s/contents"
DOCTYPES = ("document")

class SourceTypeException(Exception):
    """Source type is not Google Docs"""

class SourceInfo:

    def __init__(self, info):
        if info:
            if info["type"] == "gd":
                self.folder_id = info.get("folder_id", "")
                self.access_token = info.get("access_token", "")
                self.refresh_token = info.get("refresh_token", "")
                expiry = info.get("token_expiry", None)                
                self.token_expiry = expiry and datetime.fromtimestamp(expiry)
                return
        raise SourceTypeException

    def __call__(self):
        info = {"type": "gd",
                "folder_id": self.folder_id,
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "token_expiry": self.token_expiry and int(time.mktime(
                    self.token_expiry.timetuple()))}
        return info

    def is_complete(self):
        return bool(self.folder_id)

class Source:

    _info = None # SourceInfo

    def __init__(self, collection_id, userid):
        self._collection_id = collection_id
        self._userid = userid
        self._token = OAuth2Token(client_id=system_params.gd_oauth_client_id,
                                 client_secret=system_params.gd_oauth_client_secret,
                                 scope=GD_SCOPE,
                                 user_agent=USER_AGENT)

    def _maybe_info(self):
        collection = meta.get_collection(self._userid, self._collection_id)
        return SourceInfo(collection["source"])

    def _load(self):
        self._info = self._maybe_info()

    def _save(self):
        meta.edit_collection(self._userid, self._collection_id, source=self._info())

    def _create_info_from_token(self):
        self._info = SourceInfo({"type": "gd"})
        self._update_info_from_token()

    def _update_info_from_token(self):
        self._info.access_token = self._token.access_token
        self._info.refresh_token = self._token.refresh_token
        self._info.token_expiry = self._token.token_expiry

    def _update_token_from_info(self):
        self._token.access_token = self._info.access_token
        self._token.refresh_token = self._info.refresh_token
        self._token.token_expiry = self._info.token_expiry

    def _get_client(self):
        client = DocsClient()
        client.http_client.debug = system_params.gd_debug_mode
        self._load()
        self._update_token_from_info()
        return self._token.authorize(client)

    def oauth2_step1_get_url(self):
        return self._token.generate_authorize_url(system_params.gd_oauth_redirect_uri,
                                                 response_type='code',
                                                 state=str(self._collection_id),
                                                 access_type='offline',
                                                 approval_prompt='force')

    def oauth2_step2_run(self, code):
        self._token.redirect_uri = system_params.gd_oauth_redirect_uri
        self._token.get_access_token(code)
        self._create_info_from_token()
        self._save()

    def is_complete(self):
        return self._maybe_info().is_complete()

    def save_type(self):
        self._info = SourceInfo({"type": "gd"})
        self._save()

    def set_folder(self, folder_id):
        self._load()
        self._info.folder_id = folder_id
        self._save()
        platform.update_meta(self._collection_id)

    def get_folders(self):
        client = self._get_client()
        feed = client.get_resources(uri=FOLDERS_LIST)
        self._update_info_from_token()
        self._save()
        saved = self._info.folder_id
        r = []
        for x in feed.entry:
            folder_id = x.resource_id.text
            item = {"title":unicode(x.title.text), "id":folder_id}
            if saved:
                item["saved"] = folder_id.split(":")[1] == saved
            else:
                item["saved"] = False
            r.append(item)
        return r

    def get_docs(self):
        client = self._get_client()
        feed = client.get_resources(uri=FOLDER_CONTENT % self._info.folder_id)
        self._update_info_from_token()
        self._save()
        r = []
        for x in feed.entry:
            doctype, docid = tuple(x.resource_id.text.split(":"))
            if doctype in DOCTYPES:
                r.append({"id":docid, "title":x.title.text, "modified":x.updated.text})
        return r
