import smarttypes
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_reduction import TwitterReduction
from smarttypes.model.twitter_community import TwitterCommunity

def index(req, session, postgres_handle):
    root_user_count_tups = TwitterReduction.get_user_reduction_counts(postgres_handle)
    reductions = [TwitterReduction.get_latest_reduction(x[0].id, postgres_handle) for x in root_user_count_tups]
    return {
        'active_tab': 'social_map',
        'template_path': 'social_map/index.html',
        'reductions':reductions,
    }

def reduction(req, session, postgres_handle):
    reduction = None
    if 'reduction_id' in req.params:
        reduction_id = int(req.params['reduction_id'])
        reduction = TwitterReduction.get_by_id(reduction_id, postgres_handle)
    return {
        'active_tab': 'social_map',
        'template_path': 'social_map/reduction.html',
        'reduction':reduction,
    }

def community(req, session, postgres_handle):
    community = None
    if 'community_id' in req.params:
        community_id = int(req.params['community_id'])
        community = TwitterCommunity.get_by_id(community_id, postgres_handle)
    return {
        'active_tab': 'social_map',
        'template_path': 'social_map/community.html',
        'community':community,
    }