import os
import sys
import praw
import random

sys.path.append(os.path.abspath('../'))

from utilities.api_keys import *
from utilities.reddit_toolkit import RedditExplorer

rex = RedditExplorer(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

reddit = praw.Reddit(user_agent="user", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

def random_comments(post, number):
    comment_bodies = [tup[0] for tup in rex.all_comments_to_list(post.comments, relevance_threshold=0, max_num_comments=200)]
    return random.sample(comment_bodies, min(number, len(comment_bodies)))

def main():
    if not os.path.isdir('ground_truths'):
        os.mkdir('ground_truths')

    # Subreddits whose comments we'll use in tagging our ground truths.
    subs = ['political_discussion', 'politics', 'bluemidterm2018', 'conservative', 'republicans', 'republican', 'libertarian']

    print("Press a to save as democrat-leaning in sentiment, d for"
          " republican leaning in sentiment, or s for neutral. Q to save and quit.")

    print("Pulling comments for tagging...")

    sub = reddit.subreddit('+'.join(subs))
    posts = [post for post in sub.hot(limit=30)]
    comments = []
    for post in posts:
        title = post.title
        comments += [(title, comment) for comment in random_comments(post, 30)]

    random.shuffle(comments)
    results = ""
    for title, comment in comments:
        char = 'x'
        # Of course, it's not an error, but it helps to delineate things
        sys.stderr.write(title + "\n-------------------------------------------------\n")
        print(comment)
        while char not in 'asdq':
            char = input('')
            if char != '':
                char = char[0]
            if char == 'a':
                results += str(comment + '\tl\n')
            elif char == 'd':
                results += str(comment + '\tr\n')

            # elif char == 's':
            #    results += str(comment + '\tl\n')
            elif char == 'q':
                with open('ground_truths/saved_truths.t', 'a') as file:
                    file.write(results)
                exit()
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    main()
