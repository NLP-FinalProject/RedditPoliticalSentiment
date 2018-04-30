from utilities.reddit_toolkit import RedditExplorer
from utilities.api_keys import *

import utilities.entity_tools as et
import utilities.sentiment_toolkit as st
import praw


# Interface between flask and the core of this project.

class Interface(object):
    def __init__(self):
        self.rt = RedditExplorer()
        self.tagger = et.Tagger()

    def flask_packaging(self, *, url, number=5, num_top_com=3):
        """
        Barring changes later in the project, this will be the sole method accessed by the Flask app.
        :param url: Article URL
        :return: A list of dictionaries for the contents of each article.
        """

        def markdown_to_html(markdown):
            """
            :param markdown: A reddit comment in markdown form
            :return: A string containing the passed comment, but with the markdown
                    tags replaced by html tags. I.E., ## becomes <h2>, ** becomes <i>,
                    etc.
            """
            pass

        discussions = []
        submissions = self.rt.discussions_of_url(url)
        for submission in submissions[:number]:
            sub = self.rt.parse_submission_info(submission, num_top_comments=num_top_com)

            top_comments_processed = []

            for comment in sub['top_comments']:
                comm = {}
                comm['words'] = comment.body.split(' ')
                comm['score'] = comment.score
                comm['url'] = comment.permalink
                comm['r_words'] = set([])
                comm['l_words'] = set([])

                nps = []
                for tagged_sentence in tagger.preprocess(comment.body):
                    fully_tagged = tagger.convert(tagger.parse(tagged_sentence))
                    nps += tagger.get_nps(fully_tagged)
                affiliations = [pt.entity_to_political_party(np) for np in nps]
                for name, party in affiliations:
                    if 'Republican' in party:
                        for word in name.split(' '):
                            comm['r_words'].add(word)
                    if 'Democrat' in party:
                        for word in name.split(' '):
                            comm['l_words'].add(word)

                # Todo link to sentiment analysis

                top_comments_processed.append(comm)
            sub['top_comments'] = top_comments_processed
            discussions.append(sub)

        return discussions