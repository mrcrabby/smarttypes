
import smarttypes
import controllers
from smarttypes.utils import email_utils
import re, os
import traceback
from webob import Request
from smarttypes.utils.web_response import WebResponse
from smarttypes.utils.exceptions import RedirectException
from smarttypes.utils.postgres_handle import PostgresHandle
from smarttypes.model.twitter_session import TwitterSession
from smarttypes.model.twitter_user import TwitterUser

urls = [

    (r'^$', controllers.index),

    (r'^sign_in/?$', controllers.sign_in),
    (r'^my_account/?$', controllers.my_account),
    (r'^save_email/?$', controllers.save_email),

    (r'^blog/?', controllers.blog),

    (r'^social_map/community_features/?', controllers.social_map.community_features),
    (r'^social_map/people_features/?', controllers.social_map.people_features),

    (r'^about/?$', controllers.about),
    (r'^contact/?$', controllers.about),

    (r'^static/?', controllers.static),

    (r'^', controllers.index), #catch all
]


def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, controller in urls:
        match = re.search(regex, path)
        if match:
            request = Request(environ)
            try:
                postgres_handle = PostgresHandle(smarttypes.connection_string)
                try:
                    session = None
                    if request.cookies.get('session'):
                        session = TwitterSession.get_by_request_key(request.cookies['session'], postgres_handle)
                    response_dict = controller(request, session, postgres_handle)
                    web_response = WebResponse(request, controller.__name__, response_dict, session)
                    response_headers = web_response.get_response_headers()
                    response_string = web_response.get_response_str()
                    if getattr(postgres_handle, '_connection', False):
                        postgres_handle.connection.commit()
                    status_code = '200 OK'
                except RedirectException, (redirect_ex):
                    if getattr(postgres_handle, '_connection', False):
                        postgres_handle.connection.commit()
                    status_code = '303 See Other'
                    response_headers = [('Location', redirect_ex.redirect_url)]
                    response_string = [""]
                except:
                    if getattr(postgres_handle, '_connection', False):
                        postgres_handle.connection.rollback()
                    raise
                finally:
                    if getattr(postgres_handle, '_connection', False):
                        postgres_handle.connection.close()

                #start response
                start_response(status_code, response_headers)
                return response_string

            except Exception:
                #can't use print statements with mod_wsgi
                error_string = traceback.format_exc()
                start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
                if smarttypes.config.IS_PROD:
                    email_utils.send_email('error@smarttypes.org',
                        ['timmyt@smarttypes.org', 'kevinroth82@gmail.com'],
                        path + ' \n ' + error_string, 'smarttypes site error')
                return [error_string]

    #couldn't find it
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return ["Couldn't find the URL specified. %s" % path]
