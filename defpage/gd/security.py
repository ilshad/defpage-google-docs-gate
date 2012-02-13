from defpage.lib.authentication import get_user_info
from defpage.gd.config import system_params

def get_user(request):
    user = get_user_info(request,
                         system_params.auth_session_cookie_name,
                         system_params.sessions_url)
    return user
