
from smarttypes.model.postgres_base_model import PostgresBaseModel


class TwitterReduction(PostgresBaseModel):

    table_name = 'twitter_reduction'
    table_key = 'id'
    table_columns = [
        'root_user_id',
    ]
    table_defaults = {}

    def root_user(self):
        from smarttypes.model.twitter_user import TwitterUser
        return TwitterUser.get_by_id(self.root_user_id, self.postgres_handle)

    def communities(self):
        from smarttypes.model.twitter_community import TwitterCommunity
        return TwitterCommunity.get_by_name_value('reduction_id', self.id, self.postgres_handle)

    @classmethod
    def get_latest_reduction(cls, root_user_id, postgres_handle):
        qry = """
        select *
        from twitter_reduction
        where root_user_id = %(root_user_id)s
        order by createddate desc limit 1;
        """
        params = {'root_user_id': root_user_id}
        results = postgres_handle.execute_query(qry, params)
        if results:
            return cls(postgres_handle=postgres_handle, **results[0])
        else:
            return None

    @classmethod
    def get_ordered_id_list(cls, root_user_id, postgres_handle):
        qry = """
        select id
        from twitter_reduction
        where root_user_id = %(root_user_id)s
        order by createddate asc;
        """
        return_list = []
        params = {'root_user_id': root_user_id}
        for result in postgres_handle.execute_query(qry, params):
            return_list.append(result['id'])
        return return_list

    @classmethod
    def get_user_reduction_counts(cls, postgres_handle):
        from smarttypes.model.twitter_user import TwitterUser
        return_users = []
        qry = """
        select root_user_id, count(root_user_id) as reduction_count
        from twitter_reduction
        group by root_user_id;
        """
        for result in postgres_handle.execute_query(qry):
            user = TwitterUser.get_by_id(result['root_user_id'], postgres_handle)
            return_users.append((user, result['reduction_count']))
        return return_users

    @classmethod
    def create_reduction(cls, root_user_id, postgres_handle):
        twitter_reduction = cls(postgres_handle=postgres_handle)
        twitter_reduction.root_user_id = root_user_id
        twitter_reduction.save()
        return twitter_reduction