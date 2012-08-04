
from smarttypes.model.postgres_base_model import PostgresBaseModel
from datetime import datetime, timedelta
from smarttypes.utils import time_utils, text_parsing
import re, string, heapq, random, collections, numpy

class TwitterCommunity(PostgresBaseModel):

    table_name = 'twitter_community'
    table_key = 'id'
    table_columns = [
        'reduction_id',
        'index',
        'member_ids',
        'member_idxs',
        'coordinates',
        'community_score',
        'community_pagerank',
    ]    
    table_defaults = {}

    def get_members(self):
        return_list = []
        for i in range(len(self.member_ids)):
            user_id = self.member_ids[i]
            score = self.community_pagerank[i]
            return_list.append((score, user_id))
        return return_list
    
    def top_users(self, num_users=20, just_ids=False):
        from smarttypes.model.twitter_user import TwitterUser
        return_list = []
        score_user_id_tup_list = self.get_members()
        for score, user_id in heapq.nlargest(num_users, score_user_id_tup_list):
            if score:
                add_this = (score, user_id)
                if not just_ids: 
                    add_this = (score, 
                        TwitterUser.get_by_id(user_id, self.postgres_handle))
                return_list.append(add_this)
            else:
                break
        return return_list

    @classmethod
    def get_all(cls, reduction_id, postgres_handle):
        return cls.get_by_name_value('reduction_id', reduction_id, postgres_handle)
    
    @classmethod
    def search(cls, search_string, postgres_handle):
        #this is just a shell of a method
        #the idea is to search across all reductions and communities
        qry = """
        select *
        from twitter_community c
        join twitter_reduction r on c.reduction_id = r.id
        where c.tag_cloud
        group by r.root_user_id;
        """
        params = {'root_user_id': root_user_id}
        results = postgres_handle.execute_query(qry, params)
        if results:
            return cls(postgres_handle=postgres_handle, **results[0])
        else:
            return None
        return cls.get_by_name_value('reduction_id', reduction_id, postgres_handle)

    @classmethod
    def create_community(cls, reduction_id, index, member_ids, member_idxs, coordinates,
            community_score, community_pagerank, postgres_handle):
        twitter_community = cls(postgres_handle=postgres_handle)
        twitter_community.reduction_id = reduction_id
        twitter_community.index = index
        twitter_community.member_ids = member_ids
        twitter_community.member_idxs = member_idxs
        twitter_community.coordinates = coordinates
        twitter_community.community_score = community_score
        twitter_community.community_pagerank = community_pagerank
        twitter_community.save()
        return twitter_community
        

        
        
        