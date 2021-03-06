
from smarttypes.model.postgres_base_model import PostgresBaseModel
from types import NoneType
from datetime import datetime, timedelta
import numpy, random, heapq
import collections, csv, sys
from copy import copy
import codecs
from smarttypes.utils import time_utils
from psycopg2 import IntegrityError

class TwitterUser(PostgresBaseModel):
    table_name = 'twitter_user'
    table_key = 'id'
    table_columns = [
        'id',
        'twitter_account_created',
        'screen_name',
        'protected',
        'time_zone',
        'lang',
        'location_name',
        'description',
        'url',
        'profile_image_url',
        'following_count',
        'followers_count',
        'statuses_count',
        'favourites_count',
        'last_loaded_following_ids',
        'caused_an_error',
    ]
    table_defaults = {
        #'following_ids':[],
    }

    RELOAD_FOLLOWING_THRESHOLD = timedelta(days=14)
    TRY_AGAIN_AFTER_FAILURE_THRESHOLD = timedelta(days=31)

    @property
    def credentials(self):
        from smarttypes.model.twitter_credentials import TwitterCredentials
        creds = TwitterCredentials.get_by_twitter_id(self.id, self.postgres_handle)
        return creds
        
    def set_graph_time_context(self, at_this_datetime):
        self._at_this_datetime = at_this_datetime

    def get_graph_time_context(self):
        if not '_at_this_datetime' in self.__dict__:
            return self.last_loaded_following_ids
        else:
            return self._at_this_datetime

    @property
    def following_ids(self):
        if not '_following_ids' in self.__dict__:
            if not self.last_loaded_following_ids:
                self._following_ids = []
            else:
                pre_params = {
                    'postfix': self.last_loaded_following_ids.strftime('%Y_%U'),
                    'user_id': '%(user_id)s',
                }
                qry = """
                select *
                from twitter_user_following_%(postfix)s
                where twitter_user_id = %(user_id)s
                ;
                """ % pre_params
                params = {
                    'user_id': self.id
                }
                results = self.postgres_handle.execute_query(qry, params)
                if not results:
                    self._following_ids = []
                else:
                    self._following_ids = results[0]['following_ids']
        return self._following_ids

    @property
    def following(self):
        return self.get_by_ids(self.following_ids, self.postgres_handle)

    @property
    def following_and_expired_ids(self):
        following_in_db = self.following
        following_in_db_ids = set([x.id for x in following_in_db])
        not_in_db = set(self.following_ids).difference(following_in_db_ids)
        return_list = list(not_in_db)
        for user in following_in_db:
            if user.is_expired:
                return_list.append(user.id)
        #move on if we have more than some # in the db + not expired
        if len(self.following_ids) - len(return_list) > 1000:
            return []
        return return_list

    @property
    def is_expired(self):
        expired = True
        if self.last_loaded_following_ids and \
           (datetime.now() - self.last_loaded_following_ids) < self.RELOAD_FOLLOWING_THRESHOLD:
            expired = False
        return expired and \
               not self.caused_an_error and \
               not self.protected 

    def get_random_followie_id(self, not_in_this_list=[], attempts=0):
        random_index = random.randrange(0, len(self.following_ids))
        random_id = self.following_ids[random_index]
        if random_id in not_in_this_list and attempts < 500:
            attempts += 1
            return self.get_random_followie_id(not_in_this_list, attempts)
        else:
            return random_id

    def get_id_of_someone_in_my_network_to_load(self):
        #the people self follows
        following_and_expired_list = self.following_and_expired_ids
        if following_and_expired_list:
            random_index = random.randrange(0, len(following_and_expired_list))
            return following_and_expired_list[random_index]
        #the people self follows follows
        else:
            #print '%s: pulling second layer of followies' % self.screen_name
            tried_to_load_these_ids = []
            for i in range(150):  # give up at some point (this could be anything)
                random_following_id = self.get_random_followie_id(tried_to_load_these_ids)
                random_following = TwitterUser.get_by_id(random_following_id, self.postgres_handle)
                if random_following:
                    random_following_following_and_expired_list = random_following.following_and_expired_ids
                    if random_following_following_and_expired_list:
                        #print '%s: took %s attempts to find someone in second layer' % (self.screen_name, i)
                        return random_following_following_and_expired_list[0]
                    else:
                        tried_to_load_these_ids.append(random_following_id)
                else:
                    tried_to_load_these_ids.append(random_following_id)

    def get_latest_reduction(self):
        from smarttypes.model.twitter_reduction import TwitterReduction
        return TwitterReduction.get_latest_reduction(self.id, self.postgres_handle)

    def save_following_ids(self, following_ids):
        pre_params = {
            'postfix': datetime.now().strftime('%Y_%U'),
            'user_id': '%(user_id)s',
            'following_ids': '%(following_ids)s',}

        select_sql = """
        select * from twitter_user_following_%(postfix)s
        where twitter_user_id = %(user_id)s;
        """ % {
            'postfix': datetime.now().strftime('%Y_%U'),
            'user_id': '%(user_id)s',}

        insert_sql = """
        insert into twitter_user_following_%(postfix)s (twitter_user_id, following_ids)
        values(%(user_id)s, %(following_ids)s);
        """ % pre_params
        
        update_sql = """
        update twitter_user_following_%(postfix)s
        set following_ids = %(following_ids)s
        where twitter_user_id = %(user_id)s;
        """ % pre_params


        results = self.postgres_handle.execute_query(select_sql, {'user_id': self.id})
        if len(results):
            use_this_sql = update_sql
        else:
            use_this_sql = insert_sql

        params = {
            'user_id': self.id,
            'following_ids': following_ids,}

        #this errors occasionally, @ seemingly random times:
        #'DETAIL:  Key (twitter_user_id)=(35514918) already exists.'
        #twitter_user_id is seemingly random
        #i'm guessing this is a multiprocess race condition
        #may want to just swallow these ??
        #or maybe use a select lock, need to research how to handle this kind of thing
        try:
            self.postgres_handle.execute_query(use_this_sql, params, return_results=False)
            self.last_loaded_following_ids = datetime.now()
            self.save()
        except IntegrityError, ex:
            print """Swallowing an ERROR. 
            Assuming this was caused by a multiprocess race condition:
            %s
            """ % (ex, )


    ##############################################
    ##class methods
    ##############################################
    @classmethod
    def by_screen_name(cls, screen_name, postgres_handle):
        results = cls.get_by_name_value('screen_name', screen_name, postgres_handle)
        if results:
            return results[0]
        else:
            return None

    @classmethod
    def get_user_count_str(cls, postgres_handle):
        qry = """
        select to_char(count(*),'999G999G999G990D') as user_count
        from twitter_user
        ;
        """
        return postgres_handle.execute_query(qry)[0]['user_count']

    @classmethod
    def get_following_following_ids(cls, root_user, distance=100):
        print "Loading following_following_ids!"
        return_ids = set(root_user.following_ids)
        for following in root_user.following[:1000]:
            for following_following_id in following.following_ids[:distance]:
                return_ids.add(following_following_id)
        return list(return_ids)

    @classmethod
    def get_rooted_network(cls, root_user, postgres_handle, go_back_this_many_weeks=2, 
            start_here='now', distance=100):
        print 'Loading network in memory!'
        from collections import OrderedDict
        network = OrderedDict()
        network[root_user.id] = set(root_user.following_ids)
        if start_here == 'now':
            start_here = datetime.now()
        start_w_this_date = start_here - timedelta(days=go_back_this_many_weeks * 7)
        year_weeknum_strs = time_utils.year_weeknum_strs(start_w_this_date, go_back_this_many_weeks + 1)

        #see these:
        # - http://www.postgresql.org/docs/current/static/queries-with.html
        # - http://archives.postgresql.org/pgsql-novice/2009-01/msg00092.php
        qry = """
        WITH only_these_ids as (
            select id from unnest(%s) as id
        )
        select u.id, f.following_ids
        from twitter_user u
        join twitter_user_following_%s f on u.id = f.twitter_user_id 
        join only_these_ids on only_these_ids.id = u.id
        where u.followers_count > 10 
        ;
        """
        following_following_ids = cls.get_following_following_ids(root_user, distance=distance)
        params = {'following_following_ids':following_following_ids}
        for year_weeknum in year_weeknum_strs:
            print 'Starting %s query!' % year_weeknum
            results = postgres_handle.execute_query(qry % ('%(following_following_ids)s', 
                year_weeknum), params)
            print 'Done w/ %s query!' % year_weeknum
            for result in results:
                if result['id'] not in network:
                    network[result['id']] = set(result['following_ids'])
        return network

    @classmethod
    def upsert_from_api_user(cls, api_user, postgres_handle):
        if api_user.protected == None:
            api_user.protected = False

        model_user = cls.get_by_id(api_user.id_str, postgres_handle)
        if model_user:
            model_user.screen_name = api_user.screen_name
            model_user.protected = api_user.protected

            model_user.time_zone = api_user.time_zone
            model_user.lang = api_user.lang
            model_user.location_name = api_user.location
            model_user.description = api_user.description
            model_user.url = api_user.url
            model_user.profile_image_url = api_user.profile_image_url

            model_user.following_count = api_user.friends_count
            model_user.followers_count = api_user.followers_count
            model_user.statuses_count = api_user.statuses_count
            model_user.favourites_count = api_user.favourites_count

        else:
            properties = {
                'id': api_user.id_str,
                'twitter_account_created': api_user.created_at,
                'screen_name': api_user.screen_name,
                'protected': api_user.protected,
                'time_zone': api_user.time_zone,
                'lang': api_user.lang,
                'location_name': api_user.location,
                'description': api_user.description,
                'url': api_user.url,
                'profile_image_url': api_user.profile_image_url,
                'following_count': api_user.friends_count,
                'followers_count': api_user.followers_count,
                'statuses_count': api_user.statuses_count,
                'favourites_count': api_user.favourites_count,
            }
            model_user = cls(postgres_handle=postgres_handle, **properties)
        model_user.save()
        return model_user
