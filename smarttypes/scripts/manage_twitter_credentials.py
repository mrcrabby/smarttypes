
from datetime import datetime
import smarttypes, sys, string
from smarttypes.config import *
from smarttypes.model.twitter_credentials import TwitterCredentials
from smarttypes.model.twitter_user import TwitterUser

from smarttypes.utils.postgres_handle import PostgresHandle
postgres_handle = PostgresHandle(smarttypes.connection_string)


def list_cred_details():
    for creds in TwitterCredentials.get_all(postgres_handle):
        creds_user = creds.twitter_user
        root_user = creds.root_user
        creds_username = creds_user.screen_name if creds_user else 'None'
        root_username = root_user.screen_name if root_user else 'None'
        last_api_query = creds.last_root_user_api_query if creds.last_root_user_api_query else datetime(2000,1,1)

        print '%s %s %s' % (
            string.ljust(creds_username, 20),
            string.ljust(root_username, 20), 
            string.ljust(creds.email if creds.email else '', 30)
        )

if __name__ == "__main__":

    """
    if no args, show all creds
    if args, first arg is creds_username, second is root_username
    """
    if len(sys.argv) == 1:
        list_cred_details()

    elif len(sys.argv) == 2:
        creds_user = TwitterUser.by_screen_name(sys.argv[1], postgres_handle)
        creds = TwitterCredentials.get_by_twitter_id(creds_user.id, postgres_handle)
        creds.root_user_id = None
        creds.save()
        postgres_handle.connection.commit()

    else:
        creds_user = TwitterUser.by_screen_name(sys.argv[1], postgres_handle)
        root_user = TwitterUser.by_screen_name(sys.argv[2], postgres_handle)
        if not root_user:
            api_user = creds_user.credentials.api_handle.get_user(screen_name=sys.argv[2])
            root_user = TwitterUser.upsert_from_api_user(api_user, postgres_handle)
            postgres_handle.connection.commit()
        creds = TwitterCredentials.get_by_twitter_id(creds_user.id, postgres_handle)
        creds.root_user_id = root_user.id
        creds.save()
        postgres_handle.connection.commit()
