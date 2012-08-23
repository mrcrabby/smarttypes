
from smarttypes.model.postgres_base_model import PostgresBaseModel
from datetime import datetime, timedelta
from smarttypes.utils import time_utils, text_parsing
import re, string, heapq, random, collections, numpy
from smarttypes.utils import web_response

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

    def centroid(self):
        qry = """
        select ST_Centroid(coordinates) as centroid
        from twitter_community
        where id = %(id)s;
        """
        params = {'id': self.id}
        return self.postgres_handle.execute_query(qry, params)[0]['centroid']

    def polygon(self):
        qry = """
        --below returns none sometimes
        --select ST_Simplify(ST_MinimumBoundingCircle(coordinates), .5) as polygon

        select ST_Envelope(coordinates) as polygon
        from twitter_community
        where id = %(id)s;
        """
        params = {'id': self.id}
        return self.postgres_handle.execute_query(qry, params)[0]['polygon']

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

    def popup_html(self):
        template = web_response.loader.load('social_map/community.html')
        template_with_dict = template.generate(**{
            'community':self,
            'content_type':'text/html',
        })
        return template_with_dict.render('xhtml')

    def geojson_dict(self):
        #ST_Simplify can return none
        polygon = self.polygon()
        if type(polygon).__name__ == 'Point': return None
        return {
            "type": "Feature",
            "properties": {
                "community_id": self.id,
                "community_idx": self.index,
                "community_score":self.community_score,
                "community_size":len(self.member_ids),
                "popup_content":self.popup_html()
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": polygon.geojson_list()
            }
        }

    def get_igraph_g(self):
        from smarttypes.model.twitter_user import TwitterUser
        from smarttypes.graphreduce.reduce_graph import get_igraph_graph
        network = {}
        for score, user_id in self.get_members():
            user = TwitterUser.get_by_id(user_id, self.postgres_handle)
            network[user.id] = set(user.following_ids)
        g = get_igraph_graph(network)
        pagerank = g.pagerank(damping=0.65)
        both = zip(pagerank, g.vs['name'])
        for x,y in sorted(both):
            print x
            print TwitterUser.get_by_id(y, self.postgres_handle).screen_name


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
    def create_community(cls, reduction_id, index, member_idxs, member_ids, coordinates,
            community_score, community_pagerank, postgres_handle):
        twitter_community = cls(postgres_handle=postgres_handle)
        twitter_community.reduction_id = reduction_id
        twitter_community.index = index
        twitter_community.member_idxs = member_idxs
        twitter_community.member_ids = member_ids
        twitter_community.coordinates = coordinates
        twitter_community.community_score = community_score
        twitter_community.community_pagerank = community_pagerank
        twitter_community.save()
        return twitter_community
        

        
        
        