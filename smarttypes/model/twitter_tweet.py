

from smarttypes.model.postgres_base_model import PostgresBaseModel


class TwitterTweet(PostgresBaseModel):

    table_name = 'twitter_tweet'
    table_key = 'id'
    table_columns = [
        'id',
        'author_id',
        'retweet_count',
        'tweet_text',
    ]    
    table_defaults = {
        #'following_ids':[],
    }
    
    @classmethod
    def upsert_from_api_tweet(cls, api_tweet, postgres_handle):
            
        model_tweet = cls.get_by_id(api_tweet.id_str, postgres_handle)
        if not model_tweet:
            properties = {
                'id':api_tweet.id_str,
                'author_id':api_tweet.author.id_str,
                'retweet_count':int(str(api_tweet.retweet_count).replace('+', '')),
                'tweet_text':api_tweet.text,
            }
            model_tweet = cls(postgres_handle=postgres_handle, **properties)
            try:
                model_tweet.save()
            except Exception, ex:
                #was it inserted by another process?
                model_tweet = cls.get_by_id(api_tweet.id_str, postgres_handle)
                if not model_tweet:
                    raise Exception('Not sure whats happening?')
            
        return model_tweet

        


        
        
        
        