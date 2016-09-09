# -*- coding: utf-8 -*-
"""
Script to download data from Gnip Engagement API, particularly for Application-Only authorization.

Example
---------
        consumer_key = 'your_consumer_key'
        consumer_secret = 'you_consumer_secret'

        outfile = 'engagement_data.pkl'

        # Each request can have a maximum of 250 Tweet ID’s.
        tweet_id_list_test = ['761743895206227968', '763720881533255680', '763742526964662274']

        result = download(consumer_key, consumer_secret, tweet_id_list_0601_0818, outfile, start_i=0)


@author: Ming Zhao
Created on Thu Sep  1 10:30:04 2016
"""
from __future__ import absolute_import, division, print_function
import numpy as np
import pandas as pd
import time
from application_only_request import Application_only_request as app_request


def download(consumer_key, consumer_secret, tweet_id_list, outfile, start_i=0):
    '''Script to download data from Engagement API'''

    # Application-Only authentication can ONLY use totals
    url = 'https://data-api.twitter.com/insights/engagement/totals'
    #url = 'https://data-api.twitter.com/insights/engagement/28hr'
    #url = 'https://data-api.twitter.com//insights/engagement/historical'

    num_tweets = len(tweet_id_list)
    api_clinet = app_request(consumer_key, consumer_secret)

    result = []
    t0 = time.time()
    for i in np.arange(start_i, num_tweets, 250):
        t1 = time.time()
        end = i+250 if i+250 < num_tweets else -1
        id_list = list(tweet_id_list[i:end])
        response = api_clinet.post(url, id_list, engagement_types=["favorites","retweets", "replies"])
        if response is not None:
            sub_results = response['user_groups']
            if len(sub_results) >0:
                for k in sub_results.keys():
                    result.append([k, sub_results[k]['favorites'], sub_results[k]['replies'], sub_results[k]['retweets']])

        delta_t = time.time() - t1
        rate_progress = i / num_tweets * 100
        if round(rate_progress*100) % 100 == 0:
            print('Progress : i={0}, %={1:2.0f}; Total time lapse = {2:.0f} sec'.format(i, rate_progress, time.time() - t0))
            # save intermediate data
            col_name = ['id', 'favorites', 'replies', 'retweets']
            result_partial = pd.DataFrame(result, columns = col_name)
            result_partial.to_pickle(outfile)

        # Make sure there is at least 10 sec between 2 consecutive requests
        if delta_t <10:
            time.sleep(10 - delta_t)


    col_name = ['id', 'favorites', 'replies', 'retweets']
    result = pd.DataFrame(result, columns = col_name)
    result.to_pickle(outfile)

    return result
