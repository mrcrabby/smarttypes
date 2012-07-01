

import smarttypes
#from smarttypes.model.twitter_group import TwitterGroup
from smarttypes.model.twitter_user import TwitterUser

def index(req, session, postgres_handle):

    return {
        'active_tab': 'social_map',
        'template_path': 'social_map/index.html',
    }