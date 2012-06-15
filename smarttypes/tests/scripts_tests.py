
import smarttypes, random
from smarttypes.utils.postgres_handle import PostgresHandle
postgres_handle = PostgresHandle(smarttypes.connection_string)

from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_credentials import TwitterCredentials

from smarttypes.scripts import get_twitter_friends

#######################
#global variables

smarttypes = TwitterUser.by_screen_name('SmartTypes', postgres_handle)
smarttypes_api_handle = smarttypes.credentials.api_handle

cocacola = TwitterUser.by_screen_name('CocaCola', postgres_handle)

########################
#tests

get_twitter_friends.load_user_and_the_people_they_follow(smarttypes_api_handle, 
	smarttypes.id, postgres_handle, is_root_user=True)



