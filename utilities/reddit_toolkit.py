# Collection of tools for interacting with reddit's API

import praw

from api_keys import *

reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=CLIENT_SECRET,
                     user_agent=USER_AGENT)

# Reddit data
def discussions_of_article(url):
    return reddit.subreddit('all').search('url:' + url)

def reddit_submission(passedURL):
    return reddit.submission(url=passedURL)

# Submission data
def submission_comments(submission):
    return submission.comments

def submission_url(submission):
    return submission.url

def submission_author(submission):
    return submission.author

def submission_title(submission):
    return submission.title

def submission_score(submission):
    return submission.score

# Comment data
def comment_author(comment):
    return comment.author

def comment_body(comment):
    return comment.body

def comment_score(comment):
    return comment.score

def comment_replies(comment):
    return comment.replies

def getFirstXComments(commentList, X):
    return commentList[:X]

# Printing methods
def print_all_posts(article_url):
    for post in discussions_of_article(article_url):
        print(str(post.score) + " | (" + post.title + ") | r/" + str(post.subreddit))

def print_post_data(reddit_url):
    submission = reddit_submission(reddit_url)
    print(str(submission_score(submission)) + " | (" + submission_title(submission) + ")")
    print("")
    # print(identify_entity())
    print("---------------------------------------")
    commentList = []

    # Flatten the comment tree so it may be sorted
    for comment in submission.comments:
        # We do this check because discussion with many comments will have 'MoreComments' object which throws things off
        if type(comment).__name__ == "Comment":
            commentList.append(comment)

    # Sort comments by top, not by hot (which is the default)
    commentList.sort(key=lambda x: x.score, reverse=True)

    # Get the first up to 10 comments
    commentList = getFirstXComments(commentList, 10)

    # Print each comment
    for comment in commentList:
        print(str(comment_score(comment)) + " | (" + comment_body(comment) + ")")
        if(len(comment_replies(comment))>=1):
            print("     " + str(comment_replies(comment)[0].score) + " | (" + comment_replies(comment)[0].body + ")")

testRedditURL = "https://www.reddit.com/r/news/comments/8c0tb4/wells_fargo_faces_1b_fine_from_federal_regulators/"
testArticleURL = "https://www.usatoday.com/story/money/2018/04/13/feds-seek-1-b-settlement-wells-fargo-mortgage-auto-loan-abuses/510207002/"

# testRedditURL = "https://www.reddit.com/r/news/comments/8ccl5m/sheriff_teen_accused_of_shooting_harnett_deputy/"
# testRedditURL = "https://www.reddit.com/r/news/comments/8co1kz/white_house_says_considering_additional_sanctions/"
# testRedditURL = "https://www.reddit.com/r/news/comments/8cn6z3/turkey_warns_greece_after_flag_is_hoisted_on/"

print_all_posts(testArticleURL)
print("")
print_post_data(testRedditURL)
