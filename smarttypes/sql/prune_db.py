import smarttypes
from smarttypes.config import *
from smarttypes.utils import time_utils

from datetime import datetime, timedelta
import psycopg2
from smarttypes.utils.postgres_handle import PostgresHandle
postgres_handle = PostgresHandle(smarttypes.connection_string)


################################################
##get rid of old connections
##we have db dumps, so we do have an archive 
##if ever needed
################################################

retention_days = 30 * 4 #about 4 months
delete_before_this_date = datetime.now() - timedelta(days=retention_days)

#delete users
sql = """
delete from twitter_user 
where last_loaded_following_ids < %(delete_before_this_date)s;"""
#print sql % {'delete_before_this_date':delete_before_this_date}
postgres_handle.execute_query(sql, {'delete_before_this_date':delete_before_this_date}, return_results=False)
postgres_handle.connection.commit()

#drop tables
sql = """drop table twitter_user_following_%(postfix)s;""" 
for year_week_st in time_utils.year_weeknum_strs(delete_before_this_date, 20, ):
	#print sql % {'postfix':year_week_st}
    postgres_handle.execute_query(sql % {'postfix':year_week_st}, return_results=False)
    postgres_handle.connection.commit()
