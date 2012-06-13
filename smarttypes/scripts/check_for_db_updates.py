
#setup a remote db tunnel
import subprocess
subprocess.call('ssh timmyt@66.228.60.238 -N -f -L 5433:localhost:5432', shell=True)

from datetime import datetime
import smarttypes, sys, string
from smarttypes.config import *
from smarttypes.model.twitter_credentials import TwitterCredentials
from smarttypes.model.twitter_user import TwitterUser

from smarttypes.utils.postgres_handle import PostgresHandle
remote_postgres_handle = PostgresHandle(smarttypes.connection_string + " port='5433'")
local_postgres_handle = PostgresHandle(smarttypes.connection_string)

for creds in TwitterCredentials.get_all(remote_postgres_handle):
    creds.postgres_handle = local_postgres_handle
    creds.save()

