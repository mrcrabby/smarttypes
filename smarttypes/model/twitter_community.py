
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
        'community_edges',
        'member_ids',
        'member_scores',
        'tag_cloud',
    ]    
    table_defaults = {}
    
    def get_members(self):
        return_list = []
        for i in range(len(self.member_ids)):
            user_id = self.member_ids[i]
            score = self.member_scores[i]
            return_list.append((score, user_id))
        return return_list
    
    def top_users(self, num_users=20, just_ids=False):
        from smarttypes.model.twitter_user import TwitterUser
        return_list = []
        score_user_id_tup_list = self.get_members()
        for score, user_id in heapq.nlargest(num_users, score_user_id_tup_list):
            if score:
                add_this = (score, user_id)
                if not just_ids: add_this = (score, TwitterUser.get_by_id(user_id, self.postgres_handle))
                return_list.append(add_this)
            else:
                break
        return return_list
        

    ##############################################
    ##class methods
    ##############################################
    @classmethod
    def get_all(cls, reduction_id, postgres_handle):
        return cls.get_by_name_value('reduction_id', reduction_id, postgres_handle)
    
    @classmethod
    def create_community(cls, reduction_id, index, community_edges, 
            member_ids, member_scores, postgres_handle):
        twitter_community = cls(postgres_handle=postgres_handle)
        twitter_community.reduction_id = reduction_id
        twitter_community.index = index
        twitter_community.community_edges = community_edges
        twitter_community.member_ids = member_ids
        twitter_community.member_scores = member_scores
        twitter_community.save()
        return twitter_community
        
    @classmethod
    def mk_tag_clouds(cls, reduction_id, postgres_handle):
        print "starting community_wordcounts loop"
        community_wordcounts = {}
        all_words = set()
        for community in cls.get_all(reduction_id, postgres_handle):
            community_wordcounts[community.index] = (community, collections.defaultdict(int))
            for score, user in community.top_users(num_users=25):
                if not user.description:
                    continue
                regex = re.compile(r'[%s\s]+' % re.escape(string.punctuation))
                user_words = set()
                user.description = '' if not user.description else user.description
                user.location_name = '' if not user.location_name else user.location_name
                loc_desc = '%s %s' % (user.description.strip(), user.location_name.strip())
                for word in regex.split(loc_desc):
                    word = string.lower(word)
                    if len(word) > 2 and word not in user_words:
                        user_words.add(word)
                        all_words.add(word)
                        community_wordcounts[community.index][1][word] += (1 + (score * 5))
                        
        print "starting avg_wordcounts loop"            
        avg_wordcounts = {} #{word:avg}
        sum_words = []#[(sum,word)]
        for word in all_words:
            community_usage = []
            for community_index in community_wordcounts:
                community_usage.append(community_wordcounts[community_index][1][word])
            avg_wordcounts[word] = numpy.average(community_usage)
            sum_words.append((numpy.sum(community_usage), word))        
        
        print "starting delete stop words loop"
        for community_index in community_wordcounts:
            for word in text_parsing.STOPWORDS:
                if word in community_wordcounts[community_index][1]:
                    del community_wordcounts[community_index][1][word]     
                
        print "starting communities_unique_words loop"
        communities_unique_words = {} #{community_index:[(score, word)]}
        for community_index in community_wordcounts:
            communities_unique_words[community_index] = []
            for word, times_used in community_wordcounts[community_index][1].items():
                if times_used > 2.5:
                    usage_diff = times_used - avg_wordcounts[word]
                    communities_unique_words[community_index].append((usage_diff, word))
        
        print "starting save tag_cloud loop"
        for community_index, unique_scores in communities_unique_words.items():
            community = community_wordcounts[community_index][0]
            community.tag_cloud = [x[1] for x in heapq.nlargest(10, unique_scores)]
            community.save()
        
        return "All done!"
        
        
        