

from smarttypes.model.postgres_base_model import PostgresBaseModel
import tweepy
from smarttypes.config import *
# from smarttypes import model
from smarttypes.utils import email_utils


class TwitterCredentials(PostgresBaseModel):

    table_name = 'twitter_credentials'
    table_key = 'access_key'
    table_columns = [
        'access_key',
        'access_secret',
        'twitter_id',
        'email',
        'root_user_id',
        'last_root_user_api_query'
    ]
    table_defaults = {}

    @property
    def auth_handle(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(self.access_key, self.access_secret)
        return auth

    @property
    def api_handle(self):
        return tweepy.API(self.auth_handle)

    @property
    def twitter_user(self):
        from smarttypes.model.twitter_user import TwitterUser
        if not self.twitter_id:
            return None
        return TwitterUser.get_by_id(self.twitter_id, self.postgres_handle)

    @property
    def root_user(self):
        from smarttypes.model.twitter_user import TwitterUser
        if not self.root_user_id:
            return None
        return TwitterUser.get_by_id(self.root_user_id, self.postgres_handle)

    @classmethod
    def create(cls, access_key, access_secret, postgres_handle):
        return cls(postgres_handle=postgres_handle,
                   access_key=access_key, access_secret=access_secret).save()

    @classmethod
    def get_by_access_key(cls, access_key, postgres_handle):
        results = cls.get_by_name_value('access_key', access_key, postgres_handle)
        if results:
            return results[0]
        else:
            return None

    @classmethod
    def get_by_twitter_id(cls, twitter_id, postgres_handle):
        results = cls.get_by_name_value('twitter_id', twitter_id, postgres_handle)
        if results:
            return results[0]
        else:
            return None

    @classmethod
    def get_all(cls, postgres_handle, order_by='createddate'):

        sql_inject_protect = {
            'createddate': 'createddate desc',
            'last_root_user_api_query': "coalesce(last_root_user_api_query, '2000-01-01') asc",
        }

        qry = """
        select *
        from twitter_credentials
        order by %s;
        """ % sql_inject_protect[order_by]
        results = postgres_handle.execute_query(qry)
        return [cls(postgres_handle=postgres_handle, **x) for x in results]
