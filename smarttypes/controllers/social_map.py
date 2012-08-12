
import smarttypes, random
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_community import TwitterCommunity
from smarttypes.utils import is_int

def community_features(req, session, postgres_handle):
    reduction = None
    if req.path.split('/') > 3 and req.path.split('/')[3]:  # path looks like '/social_map/community_features/something'
        root_user = TwitterUser.by_screen_name(req.path.split('/')[3], postgres_handle)
        if root_user:
            reduction = TwitterReduction.get_latest_reduction(root_user.id, postgres_handle)
        if not reduction and is_int(req.path.split('/')[3]):
            reduction = TwitterReduction.get_by_id(req.path.split('/')[3], postgres_handle)
    return {
        'content_type': 'application/json',
        'json':reduction.get_geojson_community_features() if reduction else [],
    }

def people_features(req, session, postgres_handle):
    reduction = None
    if req.path.split('/') > 3 and req.path.split('/')[3]:  # path looks like '/social_map/people_features/something'
        root_user = TwitterUser.by_screen_name(req.path.split('/')[3], postgres_handle)
        if root_user:
            reduction = TwitterReduction.get_latest_reduction(root_user.id, postgres_handle)
        if not reduction and is_int(req.path.split('/')[3]):
            reduction = TwitterReduction.get_by_id(req.path.split('/')[3], postgres_handle)
    return {
        'content_type': 'application/json',
        'json':reduction.get_geojson_user_features() if reduction else [],
    }