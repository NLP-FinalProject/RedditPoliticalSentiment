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
        sub['comments'] = submission.comments
        return sub

    def top_comments(self, submission, num_top_comments):
        return [comment for comment in submission.comments[:num_top_comments + 1]
                    if comment.author is not None and comment.author.name != 'AutoModerator']

    def all_comments_to_list(self, submission_comments, *, relevance_threshold=10, min_length=100):
        """
        Traverses the comment tree returning a list containing all comments and their scores.

        :param submission_comments: A submission.comments object, a list of all top-level submissions
        :param relevance_threshold: The minimum absolute value of the score of a counted comment
        :param min_length: The minimum length of a comment, as sentiment analysis is less precise on shorter statements.
        :return: A list of all comments and their scores meeting the threshold remands.
        :rtype: list[(str, int)]
        """
        def comment_replies(comment):
            '''
            Recursively iterates through a comment tree
            :param comment: The root of the current comment tree
            :return: A list containing the contents and score of the given comment as well as all children comments.
            '''
            all_replies = [(comment.body, comment.score)] if abs(comment.score) > relevance_threshold \
                and len(comment.body) > min_length \
                else []

            for reply_comm in comment.replies:
                all_replies += comment_replies(reply_comm)
            return all_replies

        # The limit of 0 simply replaces the "more comments" in the tree, which can otherwise throw things off.
        submission_comments = submission_comments.replace_more(limit=0)

        comments = []
        for top_level_comment in submission_comments:
            comments += comment_replies(top_level_comment)
        return comments
