
import smarttypes, sys
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_tweet import TwitterTweet
from datetime import datetime, timedelta
from smarttypes.utils.postgres_handle import PostgresHandle


if __name__ == "__main__":

	postgres_handle = PostgresHandle(smarttypes.connection_string)

    if not len(sys.argv) > 1:
        raise Exception('Need a twitter handle.')
    else:
        screen_name = sys.argv[1]
        
    root_user = TwitterUser.by_screen_name(screen_name, postgres_handle)
    friends_file = open('/tmp/%s_twitter_friends.csv' % screen_name, 'w')
    TwitterUser.mk_following_following_csv(root_user.id, friends_file, postgres_handle)
    
    #tweets_file = open('/tmp/%s_twitter_tweets.csv')
    #TwitterUser.mk_following_tweets_csv(screen_name, tweets_file)
    