
from smarttypes.model.postgres_base_model import PostgresBaseModel


class TwitterReductionUser(PostgresBaseModel):

    table_name = 'twitter_reduction_user'
    table_key = 'id'
    table_columns = [
        'reduction_id',
        'user_id',
        'coordinates',
        'pagerank',
        'hybrid_pagerank',
    ]
    table_defaults = {}


