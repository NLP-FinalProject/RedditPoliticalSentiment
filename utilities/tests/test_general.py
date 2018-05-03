from unittest import TestCase
from utilities.api_keys import *
from utilities.sentiment_toolkit import SentimentClassifier

import utilities.entity_toolkit as et
import utilities.reddit_toolkit as rt

class TestRedditExplorer(TestCase):

    def test_reddit_explorer(self):
        reddit = rt.RedditExplorer(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        test_url = 'https://www.washingtonpost.com/world/national-security/trump-revealed-highly-classified-information-to-russian-foreign-minister-and-ambassador/2017/05/15/530c172a-3960-11e7-9e48-c4f199710b69_story.html'
        try:
            test_submission = list(reddit.discussions_of_url(test_url))[0]
        except IndexError:
            self.fail()
        sub = reddit.parse_submission_info(test_submission)
        self.assertTrue(all([item is not None] for item in sub.items()))

        if len((list(sub['comments']))) > 3:
            self.assertEqual(len(reddit.top_comments(sub['comments'], 3)), 3)
        self.assertIsNotNone(reddit.all_comments_to_list(sub['comments']))

    def test_sentiment_classifier(self):
        classifier = SentimentClassifier(load_path='../trained_models/model.tfl')
        # Test a positive statement
        self.assertEqual(classifier.predict("I love tflearn more than anything! I want to use it every day!"), 1)
        # Test a negative statement
        self.assertEqual(classifier.predict("I hate tflearn more than anything! It is the worst thing I've ever seen."),
                         -1)

    def test_party_classification(self):
        try:
            ent_linker = et.EntityLinker(path='../saved_data/entity_files/dict.json')
        except NotADirectoryError:
            self.fail()
        self.assertTrue('nazi' in ent_linker.entity_to_political_party('Adolf Hitler')[1].lower())
        self.assertTrue('democrat' in ent_linker.entity_to_political_party('Hillary Clinton')[1].lower())
        self.assertTrue('democrat' in ent_linker.entity_to_political_party('Barack Obama')[1].lower())
        self.assertTrue('republican' in ent_linker.entity_to_political_party('Donald Trump')[1].lower())
        self.assertTrue('republican' in ent_linker.entity_to_political_party('George Bush')[1].lower())


