
import random

from smarttypes.utils.mongo_web_decorator import mongo_web_decorator
from smarttypes.utils.web_response import WebResponse
from smarttypes.utils.exceptions import RedirectException
from genshi.core import Markup
from smarttypes.model.twitter_group import TwitterGroup
from smarttypes.model.twitter_user import TwitterUser


@mongo_web_decorator()
def home(request):
    return WebResponse()

@mongo_web_decorator()
def root_user(request):
    
    screen_name = request.params['screen_name']
    root_user = TwitterUser.by_screen_name(screen_name)    
    return WebResponse(
        return_dict={
            'root_user':root_user,
        }
    )


@mongo_web_decorator()
def user(request):
    
    if 'user_id' in request.params:
        user_id = int(request.params['user_id'])
        twitter_user = TwitterUser.get_by_id(user_id)
    else:
        screen_name = request.params['screen_name']
        twitter_user = TwitterUser.by_screen_name(screen_name)
    
    return WebResponse(
        return_dict={
            'twitter_user':twitter_user,
        }
    )


@mongo_web_decorator()
def group(request):
    
    if 'group_index' in request.params:
        group_index = int(request.params['group_index'])
        twitter_group = TwitterGroup.get_by_index(group_index)
    else:
        twitter_group = TwitterGroup.get_random_group()
        
    return WebResponse(
        return_dict={
            'twitter_group':twitter_group,
        }
    )



@mongo_web_decorator()
def cluster_your_network(request):
    return WebResponse()

@mongo_web_decorator()
def about(request):
    return WebResponse()

@mongo_web_decorator()
def contact(request):
    return WebResponse()


    




