import social_map  # need this
import mimetypes
import os, random
from smarttypes.config import *
from smarttypes.utils.exceptions import RedirectException
from smarttypes.utils import twitter_api_utils
from smarttypes.utils import validation_utils
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.utils import is_int


def index(req, session, postgres_handle):
    #if it's not a valid request keep reduction_id None
    #don't do work for bots that don't know what they're 
    #looking for
    reduction = None
    user_reduction_counts = TwitterReduction.get_user_reduction_counts(postgres_handle)
    random.shuffle(user_reduction_counts)

    if req.path.split('/') > 1 and req.path.split('/')[1]:  # path looks like '/something'
        root_user = TwitterUser.by_screen_name(req.path.split('/')[1], postgres_handle)
        if root_user:
            reduction = TwitterReduction.get_latest_reduction(root_user.id, postgres_handle)
        if not reduction and is_int(req.path.split('/')[1]):
            reduction = TwitterReduction.get_by_id(req.path.split('/')[1], postgres_handle)
    else:
        reduction = TwitterReduction.get_latest_reduction(user_reduction_counts[0][0].id, postgres_handle)

    return {
        'reduction_id': reduction.id if reduction and reduction.tiles_are_written_to_disk else None,
        'reduction': reduction if reduction and reduction.tiles_are_written_to_disk else None,
        'user_reduction_counts': user_reduction_counts
    }

def sign_in(req, session, postgres_handle):
    raise RedirectException(twitter_api_utils.get_signin_w_twitter_url(postgres_handle))

def my_account(req, session, postgres_handle):
    if session:
        creds = session.credentials
        if creds:
            user = creds.twitter_user
        return {}
    if 'oauth_token' in req.params and 'oauth_verifier' in req.params:
        session = twitter_api_utils.complete_signin(req.params['oauth_token'],
                                                    req.params['oauth_verifier'], postgres_handle)
        if session:
            return {'cookies': [('session', session.request_key)], 'session': session}
    return {}

def save_email(req, session, postgres_handle):
    if session and session.credentials:
        credentials = session.credentials
        if validation_utils.is_valid_email(req.params.get('email')) or not req.params.get('email'):
            credentials.email = req.params.get('email')
            credentials.save()
    raise RedirectException('/my_account')

def blog(req, session, postgres_handle):
    changed_url_map = {
        'blog/complexity_probability_social_networks_and_python': 'blog/modeling_complexity_w_python',
        'blog/graphlab_and_python_vs_complexity': 'blog/modeling_complexity_w_python',
        'blog/modeling_complexity': 'blog/modeling_complexity_w_python',
    }
    template_path = "blog/index.html"
    if req.path.find('/', 1) > 0:  # path looks like '/blog/something'
        request_path = req.path[1:]
        if not request_path.endswith('/'):
            template_path = "%s.html" % changed_url_map.get(request_path, request_path)

    d = {
        'template_path': template_path,
        'active_tab': 'blog',
    }

    #get the meta description
    f = open(os.path.dirname(os.path.dirname(__file__)) + '/templates/' + template_path)
    template_str = f.read()
    look_for_this = '<meta name="description" content="'
    start_idx = template_str.find(look_for_this) + len(look_for_this)
    end_idx = template_str.find('" />', start_idx)
    if start_idx > len(look_for_this):
        d['meta_page_description'] = template_str[start_idx:end_idx]
    return d

def about(req, session, postgres_handle):
    return {}

def static(req, session, postgres_handle):
    #apache will handle this in prod (this is for testing)
    static_path = os.path.dirname(os.path.dirname(__file__)) + req.path
    return {
        'content_type': mimetypes.guess_type(static_path)[0],
        'return_str': open(static_path).read()
    }
