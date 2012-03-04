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

    def __init__(self, sources):
        if len(sources) > 0:
            info = sources[0]
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
                "token_expiry": int(time.mktime(self.token_expiry.timetuple()))}
        return [info] # only one source currently allowed

    def is_complete(self):
        return bool(self.folder_id)

class Source:

    info = None # SourceInfo

    def __init__(self, collection_id, userid):
        self.collection_id = collection_id
        self.userid = userid
        self.token = OAuth2Token(client_id=system_params.gd_oauth_client_id,
                                 client_secret=system_params.gd_oauth_client_secret,
                                 scope=GD_SCOPE,
                                 user_agent=USER_AGENT)

    def maybe_info(self):
        collection = meta.get_collection(self.userid, self.collection_id)
        return SourceInfo(collection["sources"])

    def load(self):
        self.info = self.maybe_info()

    def save(self):
        meta.edit_collection(self.userid, self.collection_id, sources=self.info())

    def create_info_from_token(self):
        self.info = SourceInfo([{"type": "gd"}])
        self.update_info_from_token()

    def update_info_from_token(self):
        self.info.access_token = self.token.access_token
        self.info.refresh_token = self.token.refresh_token
        self.info.token_expiry = self.token.token_expiry

    def update_token_from_info(self):
        self.token.access_token = self.info.access_token
        self.token.refresh_token = self.info.refresh_token
        self.token.token_expiry = self.info.token_expiry

    def get_info(self):
        client = self.get_client()
        folder_id = self.info.folder_id
        try:
            folder_entry = client.get_entry(GET_FOLDER % folder_id)
        except RequestError as err:
            logger.info(err)
            return {u'error': err}
        return {u"folder id":folder_id, u"title":folder_entry.title}

    def oauth2_step1_get_url(self):
        return self.token.generate_authorize_url(system_params.gd_oauth_redirect_uri,
                                                 response_type='code',
                                                 state=str(self.collection_id),
                                                 access_type='offline',
                                                 approval_prompt='force')

    def oauth2_step2_run(self, code):
        self.token.redirect_uri = system_params.gd_oauth_redirect_uri
        self.token.get_access_token(code)
        self.create_info_from_token()
        self.save()

    def get_client(self):
        client = DocsClient()
        client.http_client.debug = system_params.gd_debug_mode
        self.load()
        self.update_token_from_info()
        return self.token.authorize(client)

    def get_folders(self):
        client = self.get_client()
        feed = client.get_resources(uri=FOLDERS_LIST)
        self.update_info_from_token()
        saved = self.info.folder_id
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

    def is_complete(self):
        i = self.maybe_info()
        return i.is_complete()

    def set_folder(self, folder_id):
        self.load()
        self.info.folder_id = folder_id
        self.save()
        platform.update_meta(self.collection_id)

    def get_docs(self):
        client = self.get_client()
        feed = client.get_resources(uri=FOLDER_CONTENT % self.info.folder_id)
        self.update_info_from_token()
        r = []
        for x in feed.entry:
            doctype, docid = tuple(x.resource_id.text.split(":"))
            if doctype in DOCTYPES:
                r.append({"id":docid, "title":x.title.text, "modified":x.updated.text})
        return r
