
import smarttypes, random
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_community import TwitterCommunity

def index(req, session, postgres_handle):
    reduction = None
    if req.path.split('/') > 2:  # path looks like '/social_map/something'
        root_user = TwitterUser.by_screen_name(req.path.split('/')[2], postgres_handle)
        if root_user:
            reduction = TwitterReduction.get_latest_reduction(root_user.id, postgres_handle)
    if not reduction:
        root_user = TwitterUser.by_screen_name('SmartTypes', postgres_handle)
        reduction = TwitterReduction.get_latest_reduction(root_user.id, postgres_handle)
    return {
        'active_tab': 'social_map',
        'template_path': 'social_map/reduction.html',
        'reduction':reduction,
    }

