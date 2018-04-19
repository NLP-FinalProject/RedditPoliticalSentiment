from api_keys import *

import reddit_toolkit as rt
import os
import sys
import pickle
import praw
import random

reddit = praw.Reddit(user_agent="user", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

def random_comments(post, number):
    comments

def main():
    if not os.path.isdir('ground_truths'):
        os.mkdir('ground_truths')

    # Subreddits whose comments we'll use in tagging our ground truths.
    subs = ['politics', 'bluemidterm2018', 'conservative', 'republicans', 'republican', 'libertarian']

    print("Press a to save as democrat-leaning in sentiment, right for"
          " republican leaning in sentiment, or s for neutral.")

    print("Pulling comments for tagging...")

    sub = reddit.subreddit('+'.join(subs))
    posts = [post for post in sub.hot(limit=30)]
    comments = []
    for post in posts:
        title = post.title
        comments += [(title, comment.body.strip('\n').strip('\t')) for comment in random_comments(post, 50)]
                     if comment is not None and type(comment).__name__ == "Comment"
                     and comment.author is not None
                     and comment.author.name != 'AutoModerator'
                     and 'mod' not in comment.body]

    random.shuffle(comments)
    results = ""
    for title, comment in comments:
        char = 'x'
        # Of course, it's not an error, but it helps to delineate things
        sys.stderr.write(title + "\n\n\n")
        print(comment)
        while char not in 'asdq':
            char = input('')
            if char != '':
                char = char[0]
            if char == 'a':
                results += str (comment + '\tl\n')
            elif char == 'd':
                results += str(comment + '\tr\n')
            elif char == 's':
                results += str(comment + '\tl\n')
            elif char == 'q':
                with open('ground_truths/saved_truths.t', 'a') as file:
                    file.write(results)
                exit()
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    main()
