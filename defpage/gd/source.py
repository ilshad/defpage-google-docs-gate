import logging
from gdata.gauth import OAuth2Token
from gdata.docs.client import DocsClient
from gdata.client import RequestError
from defpage.gd.config import system_params

logger = logging.getLogger("defpage.gd")

GD_SCOPE = "https://docs.google.com/feeds/"
USER_AGENT = ""
GET_FOLDER = "https://docs.google.com/feeds/default/private/full/folder:%s"

class Source(object):

    source = None

    def __init__(self, collection_id):
        self.collection_id = collection_id
        self.token = OAuth2Token(client_id=system_params.gd_oauth_client_id,
                                 client_secret=system_params.gd_oauth_client_secret,
                                 scope=GD_SCOPE,
                                 user_agent=USER_AGENT)


    def get_info(self):
        client = self._get_client()
        folder_id = self.source["folder_id"]
        try:
            folder_entry = client.get_entry(GET_FOLDER % folder_id)
        except RequestError as err:
            logger.info(err)
            return {u'error': err}
        return {u"folder id":folder_id, u"title":folder_entry.title}

    def get_settings_url(self):
        return "/collection/%s/select_folder" % self.collection_id

    def oauth2_step1_get_url(self):
        return self.token.generate_authorize_url(system_params.gd_oauth_redirect_uri,
                                                 response_type='code',
                                                 state=str(self.collection_id),
                                                 access_type='offline',
                                                 approval_prompt='force')

    def oauth2_step2_run(self, userid, code):
        self.token.redirect_uri = system_params.gd_oauth_redirect_uri
        self.token.get_access_token(code)

        save_source(userid,
                    self.collection_id,
                    self.token.access_token,
                    self.token.refresh_token,
                    self.token.token_expiry)

    def _remember(self):
        self.source = get_googledocs_source(self.collection_id)

    def _get_client(self):
        # gdata-2.0.15
        client = DocsClient()
        client.http_client.debug = system_params.gd_debug_mode
        self._remember()

        # get tokens form database
        self.token.access_token = self.imp.access_token
        self.token.refresh_token = self.imp.refresh_token
        self.token.token_expiry = self.imp.token_expiry

        r = self.token.authorize(client)
        return r

    # set tokens into database after refreshing
    def _update(self):
        save_access_token(self.token.access_token, self.token.token_expiry)
        save_refresh_token(self.token.refresh_token)

    def get_folders(self):
        client = self._get_client()
        feed = client.get_resources(uri='/feeds/default/private/full/-/folder')
        self._update()
        saved = self.source["folder_id"]
        r = []
        for x in feed.entry:
            folder_id = x.resource_id.text
            item = {'title':unicode(x.title.text), 'id':folder_id}
            if saved:
                item["saved"] = folder_id.split(":")[1] == saved
            else:
                item["saved"] = False
            r.append(item)
            print item
        return r

def get_googledocs_source(collection_id):
    pass

def save_source(userid, collection_id, access_token, refresh_token, token_expiry):
    print "Saving source. userid:%s, colleciton_id:%s, access_token:%s, refresh_token:%s, token_expiry:%s" % (userid, collection_id, access_token, refresh_token, token_expiry)

def save_access_token(access_token, token_expiry):
    pass

def save_refresh_token(refresh_token):
    pass
