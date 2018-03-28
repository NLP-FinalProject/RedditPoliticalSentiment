# Collection of tools for interacting with reddit's API

import praw

from api_keys import *

reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)

def discussions_of_article(url):
    return reddit.subreddit('all').search('url:' + url)
