from utilities.api_keys import *
from utilities.reddit_toolkit import RedditExplorer
from utilities.sentiment_toolkit import SentimentClassifier

import utilities.entity_toolkit as et


# Interface between flask and the core of this project.

class Interface(object):
    def __init__(self, abs_path=""):
        self.rt = RedditExplorer(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.tagger = et.Tagger()
        self.sentiment = SentimentClassifier(load_path=abs_path + 'sentiment_files/model.tfl')
        self.ent_linker = et.EntityLinker()

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

        # Process the number of discussions described above
        discussions = []
        submissions = self.rt.discussions_of_url(url)
        for submission in submissions[:number]:
            sub = self.rt.parse_submission_info(submission)
            sub['top_comments'] = {}

            for comment in self.rt.top_comments(submission, num_top_com):
                comm = {
                        'words': comment.body.split(' '),
                        'score': comment.score,
                        'url': comment.permalink,
                        'r_words': set([]),
                        'l_words': set([]),
                        }

                nps = []
                for tagged_sentence in self.tagger.preprocess(comment.body):
                    fully_tagged = self.tagger.convert(self.tagger.parse(tagged_sentence))
                    nps += self.tagger.get_nps(fully_tagged)
                affiliations = [self.ent_linker.entity_to_political_party(np) for np in nps]
                for name, party in affiliations:
                    if 'Republican' in party:
                        for word in name.split(' '):
                            comm['r_words'].add(word)
                    if 'Democrat' in party:
                        for word in name.split(' '):
                            comm['l_words'].add(word)

                # TODO: Sentence-wise sentiment analysis on comment.
                sub['top_comments'].append(comm)

            discussions.append(sub)

        return discussions
