
"""
think about circular references
"""

import smarttypes, psycopg2
from smarttypes.model.ppygis import Geometry
from smarttypes.utils.postgres_handle import PostgresHandle
postgres_handle = PostgresHandle(smarttypes.connection_string)

sql = """
select pg_type.oid from pg_type where typname = 'geometry';
"""
geometry_oid = postgres_handle.execute_query(sql)[0]['oid']
GEOMETRY = psycopg2.extensions.new_type((geometry_oid, ), "GEOMETRY", Geometry.read_ewkb)
psycopg2.extensions.register_type(GEOMETRY)