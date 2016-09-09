# -*- coding: utf-8 -*-
"""
This class implements Twitter's Application-only authentication and incorporate it to the Requests package.

Example:
        from application_only_request import Application_only_request as app_request
        api_client = app_request(consumer_key, consumer_secret)
        response = api_client.post(url, tweet_id_list, engagement_types=["favorites","retweets", "replies"])

@author: Ming Zhao
Created on Wed Aug 31 15:33:30 2016
"""
from __future__ import absolute_import, division, print_function
import base64
import requests as req

try:
    # Python 3+
    from urllib.error import HTTPError
except ImportError:
    # Python 2x
    from urllib2 import HTTPError


BEARER_TOKEN_URL = 'https://api.twitter.com/oauth2/token'

class Application_only_request(object):
    '''This class implements Twitter's Application-only authentication and incorporate it to the Requests package.

    **NOTE**: your application ID has to be authorized by Twitter to be able to use the API. Contact your Twitter
              representitive for authorization.

    *Note2:*: only has 'post' method at present, will add 'get' later on.
    '''

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = None


    def _get_access_token(self):
        '''Obtain a bearer token'''
        bearer_token = '{}:{}'.format(self.consumer_key, self.consumer_secret)
        encoded_bearer_token = base64.b64encode(bearer_token.encode('utf-8'))
        headers = {'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8',
                   'Authorization':'Basic {}'.format(encoded_bearer_token.decode('utf-8'))}
        request_data = 'grant_type=client_credentials'.encode('utf-8')

        try:
            response = req.post(BEARER_TOKEN_URL, data=request_data, headers=headers)
            access_token = response.json()['access_token']
            print('--> Successfully obtained bearer token for authentication!')
        except HTTPError:
            if not response.ok:
                print('{0}\n Error Reason: {1} \n{2}'.format(response, response.reason, response.json()['errors']))
            raise
        return access_token


    def post(self, url, tweet_id_list, engagement_types=["favorites","retweets", "replies"], **kwargs):
        '''Make POST request to url.

        Parameters
        --------------
        tweet_id_list: list of str
            A list of tweet id strings, e.g., ['761743895206227968']
        engagement_types: list of str
            A list of engagement types. Default list is for un-owned tweets.
            For owned tweets more metrics are available, e.g, ["impressions", "engagements","favorites","retweets", "replies"]
        **kwargs: keywords
            Keywords from requests.post(), e.g., requests.post(url, json=data_in_json_format, data=data, json=json, headers=headers)

        '''
        if self.access_token is None:
            self.access_token = self._get_access_token()

        # Now make request with authentication
        headers = {'Accept-Encoding': 'gzip', 'Authorization':'Bearer {}'.format(self.access_token)}

        # Each request can have a maximum of 250 Tweet ID’s.
        #tweet_id_list = ['761743895206227968']

        data = {
                "tweet_ids": tweet_id_list,
                  "engagement_types": engagement_types,
                "groupings": {
                  "user_groups": {
                    "group_by": ["tweet.id", "engagement.type"]
                  }
                }
              }
        try:
            response = req.post(url, headers=headers, json=data, **kwargs)
            if response.ok:
                return response.json()
        except HTTPError:
            if not response.ok:
                print('{0}\n Error Reason: {1} \n{2}'.format(response, response.reason, response.json()['errors']))
            return None

