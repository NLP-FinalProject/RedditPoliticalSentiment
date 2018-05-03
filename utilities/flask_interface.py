from urllib.error import URLError
from collections import Counter
from json.decoder import JSONDecodeError
from nltk import sent_tokenize
from utilities.api_keys import *
from utilities.reddit_toolkit import RedditExplorer
from utilities.sentiment_toolkit import SentimentClassifier

import utilities.entity_toolkit as et

junk_words = {'guys', 'one', 'center', 'ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very', 'having', 'with', 'they', 'own', 'an', 'be', 'some', 'for', 'do', 'its', 'yours', 'such', 'into', 'of', 'most', 'itself', 'other', 'off', 'is', 's', 'am', 'or', 'who', 'as', 'from', 'him', 'each', 'the', 'themselves', 'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more', 'himself', 'this', 'down', 'should', 'our', 'their', 'while', 'above', 'both', 'up', 'to', 'ours', 'had', 'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', 'and', 'been', 'have', 'in', 'will', 'on', 'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', 'not', 'now', 'under', 'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few', 'whom', 't', 'being', 'if', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was', 'here', 'than'}

# Interface between flask and the core of this project.

class Interface(object):
    def __init__(self, abs_path=""):
        self.rt = RedditExplorer(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.ent_linker = et.EntityLinker(path=abs_path+'saved_data/entity_files/dict.json')
        self.sentiment = SentimentClassifier(load_path=abs_path + 'trained_models/model.tfl')

    def flask_packaging(self, *, url, max_number=5, num_top_com=3):
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

        def heuristic_for_comment(comment, score, parent_party=0):
            val = 0
            nps = self.ent_linker.get_continuous_chunks(comment)[:-1]
            try:
                affiliations = [self.ent_linker.entity_to_political_party(np) for np in nps]
                affiliations = [x for x in affiliations if x is not None]
            except (ConnectionError, URLError, JSONDecodeError) as e:
                return 0
            party_count = Counter([affiliation[1] for affiliation in affiliations])
            try:
                most_common_party = party_count.most_common(1)[0][0]
                party_val = self.ent_linker.political_party_to_value(most_common_party)
                if party_val != 0:
                    val += score*party_val
            except IndexError:
                val = 0

            if val != 0:
                new_val = self.sentiment.predict(comment)
                val = val*new_val

            return val

        # Process the number of discussions described above
        discussions = []
        submissions = self.rt.discussions_of_url(url)
        for submission in submissions[:max_number]:
            sub = self.rt.parse_submission_info(submission)
            sub['top_comments'] = []



            for comment in self.rt.top_comments(submission.comments, num_top_com):
                comm = {
                        'words': comment.body.split(' '),
                        'score': comment.score,
                        'url': comment.permalink,
                        'r_words': set([]),
                        'l_words': set([]),
                        }
                nps = self.ent_linker.get_continuous_chunks(comment.body)[:-1]
                affiliations = [self.ent_linker.entity_to_political_party(np) for np in nps if
                                self.ent_linker.entity_to_political_party(np) is not None]

                for affiliation in affiliations:
                    if "Republican Party" == affiliation[1]:
                        for word in affiliation[0].lower().split(' '):
                            comm['r_words'].add(word.lower())
                    if "Democratic Party" == affiliation[1]:
                        for word in affiliation[0].lower().split(' '):
                            comm['l_words'].add(word.lower())
                sub['top_comments'].append(comm)

            # We limit the number of response comments for the sake of reducing computational complexity.
            for comment, score in self.rt.all_comments_to_list(submission.comments, max_num_comments=100):
                mod = heuristic_for_comment(comment, score)
                if mod > 0:
                    sub['r_percentage'] += mod
                else:
                    sub['l_percentage'] += abs(mod)

            total = (sub['r_percentage']+sub['l_percentage'])
            sub['r_percentage'] = sub['r_percentage']/total*100
            sub['l_percentage'] = sub['l_percentage']/total*100

            discussions.append(sub)
        return discussions
