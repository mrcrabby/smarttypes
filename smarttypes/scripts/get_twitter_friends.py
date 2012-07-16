
from multiprocessing import Process
import smarttypes
from smarttypes.config import *
from smarttypes.utils.postgres_handle import PostgresHandle
from smarttypes.model.twitter_user import TwitterUser
from smarttypes.model.twitter_credentials import TwitterCredentials
from smarttypes.utils.twitter_api_utils import get_rate_limit_status
from datetime import datetime
import tweepy
from tweepy import TweepError


def load_user_and_the_people_they_follow(creds, user_id, postgres_handle):

    remaining_hits_threshold = 10
    api_handle = creds.api_handle
    root_user = creds.root_user
    is_root_user = False
    if root_user.id == user_id:
        is_root_user = True

    remaining_hits, reset_time = get_rate_limit_status(api_handle)
    if remaining_hits < remaining_hits_threshold:
        raise Exception("%s: remaining_hits less than threshold!" % root_user.screen_name)

    try:
        api_user = api_handle.get_user(user_id=user_id)
    except TweepError, ex:
        print "%s: api_handle.get_user(%s) got a TweepError %s" % (root_user.screen_name, user_id, ex)
        if 'Sorry, that page does not exist' in str(ex) or 'User has been suspended' in str(ex):
            print 'setting caused_an_error'
            model_user = TwitterUser.get_by_id(user_id, postgres_handle)
            if not model_user:
                properties = {'id': user_id, 'screen_name': user_id}
                model_user = TwitterUser(postgres_handle=postgres_handle, **properties)
                model_user.save()
                postgres_handle.connection.commit()
            model_user.caused_an_error = datetime.now()
            model_user.save()
            postgres_handle.connection.commit()
        return None

    model_user = TwitterUser.upsert_from_api_user(api_user, postgres_handle)
    postgres_handle.connection.commit()
    screen_name = model_user.screen_name

    if api_user.protected:
        print "%s: %s is protected." % (root_user.screen_name, screen_name)
        return model_user

    following_ids = []
    print "%s: loading the people %s follows." % (root_user.screen_name, screen_name)
    try:
        max_pages = 5 if is_root_user else 1
        following_id_pages = tweepy.Cursor(api_handle.friends_ids, user_id=user_id).pages(max_pages)
        for following_ids_page in following_id_pages:
            following_ids += [str(x) for x in following_ids_page]
    except TweepError, ex:
        print "%s: loading the people %s follows, got a TweepError: %s" % (root_user.screen_name, screen_name, ex) 
        if str(ex) in ["Not authorized", "Sorry, that page does not exist"]:
            print "%s: setting caused_an_error for %s" % (root_user.screen_name, screen_name)
            model_user.caused_an_error = datetime.now()
            model_user.save()
            postgres_handle.connection.commit()
            return model_user
    model_user.save_following_ids(following_ids)
    postgres_handle.connection.commit()
    return model_user


def pull_some_users(access_key):
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    creds = TwitterCredentials.get_by_access_key(access_key, postgres_handle)
    root_user = load_user_and_the_people_they_follow(creds, creds.root_user_id, postgres_handle)
    
    
    load_this_user_id = root_user.get_id_of_someone_in_my_network_to_load()
    while load_this_user_id:
        load_user_and_the_people_they_follow(creds, load_this_user_id, postgres_handle)
        load_this_user_id = root_user.get_id_of_someone_in_my_network_to_load()
        #load_this_user_id = None
    print "Finished loading all related users for %s!" % root_user.screen_name


if __name__ == "__main__":
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    max_processes = 8
    i = 0
    for creds in TwitterCredentials.get_all(postgres_handle, order_by='last_root_user_api_query'):
        if i >= max_processes:
            break

        #this can happen because this script is run on a different db than the webserver
        #this is only a temporary problem because i'm poor
        #see scripts/check_for_db_updates.py - root_user code for related research
        if creds.twitter_id and not creds.twitter_user:
            TwitterUser.upsert_from_api_user(creds.api_handle.me(), postgres_handle)
            postgres_handle.connection.commit()

        if creds.root_user_id and not creds.root_user:
            root_user = creds.api_handle.get_user(user_id=creds.root_user_id)
            TwitterUser.upsert_from_api_user(root_user, postgres_handle)
            postgres_handle.connection.commit()

        if creds.root_user_id:
            print "Starting a process to load root user: %s" % creds.root_user.screen_name
            creds.last_root_user_api_query = datetime.now()
            creds.save()
            postgres_handle.connection.commit()
            p = Process(target=pull_some_users, args=(creds.access_key,))
            p.start()
            i += 1
