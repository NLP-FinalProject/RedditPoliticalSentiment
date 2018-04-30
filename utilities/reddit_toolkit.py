import praw

class RedditExplorer(object):

    def __init__(self, *, client_id, client_secret):
        self.reddit = praw.Reddit(user_agent="user", client_id=client_id, client_secret=client_secret)

    # Reddit data
    def discussions_of_url(self, url):
        """
        :param url: A string url pointing to a news article
        :return: A listing generator which returns submissions.
        """
        return self.reddit.subreddit('all').search('url:' + url)

    def parse_submission_info(self, submission, num_top_comments):
        """
        Parse the relevant details of a submission into a subionary, to avoid unnecessary details.
        :param submission: A :class:`~.Submission` object
        :return: A subionary containing title, subreddit, scoe, url comment_count, top_comments, and comments
        """
        sub = {}
        submission.comment_sort = 'top'
        sub['title'] = submission.title
        sub['subreddit'] = submission.subreddit
        sub['score'] = submission.score
        sub['url'] = 'https://reddit.com' + submission.permalink
        sub['comment_count'] = submission.num_comments
        sub['comments'] = submission.comments

        # Sometimes the top post is a sticky or mod post, which should be ignored.
        sub['top_comments'] = [comment for comment in sub['comments'][:num_top_comments+1]
                        if comment.author is not None and comment.author.name != 'AutoModerator']

        return sub
