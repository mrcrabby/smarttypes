
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


def load_user_and_the_people_they_follow(api_handle, user_id, postgres_handle, 
        is_root_user=False, remaining_hits_threshold=10):

    print "Attempting to load user %s." % user_id
    remaining_hits, reset_time = get_rate_limit_status(api_handle)
    if remaining_hits < remaining_hits_threshold:
        raise Exception("remaining_hits less than threshold %s" % user_id)

    try:
        api_user = api_handle.get_user(user_id=user_id)
    except TweepError, ex:
        print "**api_handle.get_user got a TweepError: %s." % ex
        return None

    model_user = TwitterUser.upsert_from_api_user(api_user, postgres_handle)
    postgres_handle.connection.commit()
    screen_name = model_user.screen_name

    if api_user.protected:
        print "\t %s is protected." % screen_name
        return model_user

    following_ids = []
    print "Loading the people %s follows." % screen_name
    try:
        max_pages = 5 if is_root_user else 1
        following_id_pages = tweepy.Cursor(api_handle.friends_ids, user_id=user_id).pages(max_pages)
        for following_ids_page in following_id_pages:
            following_ids += [str(x) for x in following_ids_page]
    except TweepError, ex:
        print "**Loading the people %s follows, got a TweepError: %s" % (screen_name, ex) 
        if str(ex) in ["Not authorized", "Sorry, that page does not exist"]:
            print "\t Setting caused_an_error for %s." % screen_name
            model_user.caused_an_error = datetime.now()
            model_user.save()
            postgres_handle.connection.commit()
            return model_user
    model_user.save_following_ids(following_ids)
    postgres_handle.connection.commit()
    return model_user


def pull_some_users(creds_user_id):
    postgres_handle = PostgresHandle(smarttypes.connection_string)
    creds_user = TwitterUser.get_by_id(creds_user_id, postgres_handle)
    if not creds_user:
        raise Exception('Creds User ID: %s not in our DB!' % creds_user_id)
    if not creds_user.credentials:
        raise Exception('%s does not have api credentials!' % creds_user.screen_name)
    api_handle = creds_user.credentials.api_handle
    root_user = load_user_and_the_people_they_follow(api_handle, creds_user.credentials.root_user_id, 
        postgres_handle, is_root_user=True)
    load_this_user_id = root_user.get_id_of_someone_in_my_network_to_load()
    while load_this_user_id:
        load_user_and_the_people_they_follow(api_handle, load_this_user_id, postgres_handle)
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
            p = Process(target=pull_some_users, args=(creds.twitter_id,))
            p.start()
            i += 1
