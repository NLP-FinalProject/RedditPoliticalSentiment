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
        submissions = self.reddit.subreddit('all').search('url:' + url)
        return list(submissions)


    def parse_submission_info(self, submission):
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
        sub['r_percentage'] = 0.00
        sub['l_percentage'] = 0.00
        # We'll seed it with these keys, partially because they're sometimes missed
        # as they can be adjectives as well as nouns.
        sub['r_words'] = {'republican', 'republicans', 'gop'}
        sub['l_words'] = {'democrats', 'democrat', 'dems'}
        return sub

    def top_comments(self, comments, num_top_comments=3):
        top_comments = []
        for comment in comments:
            if comment.author is not None and comment.author.name != 'AutoModerator':
                top_comments.append(comment)
            if len(top_comments) > num_top_comments:
                break
        return top_comments

    def all_comments_to_list(self, submission_comments, *, relevance_threshold=10, min_length=100,
                             max_num_comments=100):
        """
        Traverses the comment tree returning a list containing all comments and their scores.

        :param submission_comments: A submission.comments object, a list of all top-level submissions
        :param relevance_threshold: The minimum absolute value of the score of a counted comment
        :param min_length: The minimum length of a comment, as sentiment analysis is less precise on shorter statements.
        :return: A list of all comments and their scores meeting the threshold remands.
        :rtype: list[(str, int)]

        # TODO: This does not retrieve all comments on very large threads. Does this matter?

        """
        all_comments = submission_comments.list()
        key_comments = [(comment.body, comment.score) for comment in all_comments if
                        not isinstance(comment, praw.models.reddit.more.MoreComments)
                        and comment.author is not None
                        and comment.author.name != 'AutoModerator'
                        and abs(comment.score) > relevance_threshold
                        and len(comment.body) > min_length][:max_num_comments]
        return key_comments
