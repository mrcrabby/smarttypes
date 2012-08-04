
from smarttypes.model.postgres_base_model import PostgresBaseModel


#http://stackoverflow.com/questions/6117646/insert-into-and-string-concatenation-with-python
# sql = '''
#    INSERT INTO foo (point_geom, poly_geom)
#    VALUES (ST_PointFromText(%s, 4326), ST_GeomFromText(%s, 4326))'''
# params = ['POINT( 20 20 )', 'POLYGON(( 0 0, 0 10, 10 10, 10 0, 0 0 ))']
# cur.execute(sql, params)

#regroup data in a MULTI
#http://www.bostongis.com/postgis_dump.snippet
# SELECT stusps, ST_Multi(ST_Collect(f.the_geom)) as singlegeom 
# FROM (
#     SELECT stusps, (ST_Dump(the_geom)).geom As the_geom 
#     FROM somestatetable
# ) As f 
# GROUP BY stusps

class TwitterReduction(PostgresBaseModel):

    table_name = 'twitter_reduction'
    table_key = 'id'
    table_columns = [
        'root_user_id',
        'member_ids',
        'coordinates',
        'pagerank',
        'hybrid_pagerank',
        'translate_rotate_mask',
    ]
    table_defaults = {}

    def root_user(self):
        from smarttypes.model.twitter_user import TwitterUser
        return TwitterUser.get_by_id(self.root_user_id, self.postgres_handle)

    def communities(self):
        from smarttypes.model.twitter_community import TwitterCommunity
        communities = TwitterCommunity.get_by_name_value('reduction_id', self.id, 
            self.postgres_handle)
        return sorted(communities, key=lambda k: k.community_score, reverse=True)

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
    def create_reduction(cls, root_user_id, member_ids, coordinates, pagerank, 
            hybrid_pagerank, translate_rotate_mask, postgres_handle):
        twitter_reduction = cls(postgres_handle=postgres_handle)
        twitter_reduction.root_user_id = root_user_id
        twitter_reduction.member_ids = member_ids
        twitter_reduction.coordinates = coordinates
        twitter_reduction.pagerank = pagerank
        twitter_reduction.hybrid_pagerank = hybrid_pagerank
        twitter_reduction.translate_rotate_mask = translate_rotate_mask
        twitter_reduction.save()
        return twitter_reduction
