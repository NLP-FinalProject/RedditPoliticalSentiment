# Collection of the frequently called functions we'll be using for entity linking

from nltk import ChunkParserI, ClassifierBasedTagger
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk.corpus import conll2000
from nltk.stem.snowball import SnowballStemmer
from wikidata.client import Client

from bs4 import BeautifulSoup
import nltk
import nltk.data
import nltk.tokenize
import os
import re
import random
import requests
import sys
import wikipedia
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load/generate requisite nltk files


# Load/generate requisite nltk files
try:
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
except LookupError:
    nltk.download('punkt')
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


class EntityLinker(object):
    def __init__(self, *, path='saved_data/entity_files/dict.json'):
        self.path = path

        # If file exists
        if os.path.isfile(path):
            # Load json file into dictionary
            self.load_dictionary()

        # If parent folder exists
        else:
            self.ent_dict = {}
            # Save dictionary to json file
            self.save_dictionary()

    def load_dictionary(self):
        """
        :action: Saves dictionary to json file
        :return: None
        """
        self.ent_dict = dict(json.load(open(self.path)))

    def save_dictionary(self):
        """
        :action: Loads json file into dictionary
        :return: None
        """
        with open(self.path, 'w') as outfile:
            json.dump(self.ent_dict, outfile)

    def pretty_print_json(self, ent_dict):
        """
        :action: Pretty prints dictionary to console
        :param ent_dict: Diciontary containing previously affiliated entities
        :return: None
        """
        print(json.dumps(ent_dict, indent=4, sort_keys=True))


    """ ADDTIONAL ENTITY TOOLS WITH THE PROF API, NOT TESTED OR INTEGRATED"""

    def identify_entity(self, sentence):
        """
        :param sentence:
        :return: A list of entities and events in the order they appear in the sentence
        """
        serviceurl = 'https://blender04.cs.rpi.edu/~jih/cgi-bin/ere.py'
        payload = {'textcontent': sentence}
        # verify=False makes it so a HTTPS certificate is not required for the request
        r = requests.get(serviceurl, params=payload, verify=False)

        parsed_html = BeautifulSoup(r.text, "html.parser")
        # We are only concerned about the div lines as that's where the entities and events are in the HTML
        mentions = parsed_html.findAll('div')

        # Our list of entities and events
        taggedMentions = []

        # For each mention in sentence
        for i in mentions:
            # If it is an entity like "George Bush"
            if (str(i).startswith("<div id=\"d")):
                entityID = re.sub("(.+Entity ID: )|(<br/>.+)", "", str(i))
                entityMention = re.sub("(.+Entity Mention: )|(<br/>.+)", "", str(i))
                entityMentionType = re.sub("(.+Entity Mention Type: )|(<br/>.+)", "", str(i))
                entityType = re.sub("(.+Entity Type: )|(<br/>.+)", "", str(i))
                entityClass = re.sub("(.+Entity Class: )|(<br/>.+)", "", str(i))
                taggedMentions.append(['Entity', entityID, entityMention, entityMentionType, entityType, entityClass])
            # If it is an event like "meet"
            elif (str(i).startswith("<div id=\"e")):
                eventID = re.sub("(.+Event ID: )|(<br/>.+)", "", str(i))
                trigger = re.sub("(.+Trigger: )|(<br/>.+)", "", str(i))
                eventType = re.sub("(.+Event Type: )|(<br/>.+)", "", str(i))
                eventSubtype = re.sub("(.+Event Subtype: )|(<br/>.+)", "", str(i))
                genericity = re.sub("(.+Genericity: )|(<br/>.+)", "", str(i))
                modality = re.sub("(.+Modality: )|(<br/>.+)", "", str(i))
                polarity = re.sub("(.+Polarity: )|(<br/>.+)", "", str(i))
                tense = re.sub("(.+Tense: )|(<br/>.+)", "", str(i))
                arguments = re.sub("(.+Arguments: )|(<br/>.+)", "", str(i))
                person = re.sub("(.+;\">)|(</a>.+)", "", str(i))
                taggedMentions.append(['Event', eventID, trigger, eventType, eventSubtype, genericity, modality, polarity, tense, arguments, person])
        return taggedMentions

    """ END UNTESTED ENTITIY TOOLS"""


    def get_all_entity_political_parties(self, entity_list):
        """
        :param entityList: the list that is returned from identify_entity when passed an input String
        :return: a list of tuples containing the normalized name for the entity and their party
        """
        entity_party_list = []
        for e in entity_list:
            entity_party_list.append(self.entity_to_political_party(e[2]))
        return entity_party_list


    def page_title_to_political_party(self, title):
        """
        :param wiki: a valid WikipediaPage object
        :return: A string representing the political party or affiliation of the entity described in the wikipage, if
                available. Otherwise, a string 'None' is returned.
        """
        # Go through wikipedia json to get the id for wikidata
        resp = requests.get(url='https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles=' + title)
        data = resp.json()
        page_data = data['query']['pages'][list(data['query']['pages'].keys())[0]]
        page_properties = page_data['pageprops']
        item_id = page_properties['wikibase_item']

        # With item id in tow, extract political affiliation
        client = Client()
        entity = client.get(item_id, load=True)
        try:
            party_entity = entity.getlist(client.get('P102'))[0]
            return str(party_entity.label)
        except:
            return 'None found'


    def entity_to_political_party(self, entity, type='Person', previous_subject_titles=[]):
        """
        :param entity: String containing the name of the entity to be passed
        :return: A tuple containing the name of the matching page and that page's affiliation
        """
        # If already in dictionary, return dict entry instead of looking on Wikipedia
        if entity in self.ent_dict:
            return self.ent_dict[entity]

        pages = wikipedia.search(entity)
        # With the exception of Morrissey and Madonna, people have two words in their names
        if type =='Person':
            page_titles = [p.split() for p in pages]
            page_titles = [[w for w in title if '(' not in w] for title in page_titles]
            page_titles = [' '.join(title) for title in page_titles if len(title) >= 2]
        else:
            sys.stderr.write("ERROR: Only person entity-type supported")
            return None

        # If any of the results have been previously discussed in the thread, those should be given priority
        new_titles = [title for title in page_titles if title not in previous_subject_titles]
        page_titles = previous_subject_titles + new_titles

        # Iterate through these titles
        for title in page_titles:
            found_party = self.page_title_to_political_party(title)
            if found_party != 'None found':
                self.ent_dict[entity] = (title, found_party)
                self.save_dictionary()
                return title, found_party
        return 'No political figure', 'None found'

    def political_party_to_value(self, party):
        """
        :param party: A string representing the name of a political party
        :return: A value [-1.0, 1.0] representing this affiliation.
        """
        # TODO: More nuanced approach, use wikipedia API rather than fixed values
        if 'republican' in party.lowercase():
            return 1
        elif 'democrat' in party.lowercase():
            return -1
        else:
            sys.stderr.write('ERROR: Method not yet completed.\n Cannot handle ' + party)
            return 0


class Tagger(ChunkParserI):
    def __init__(self, data=None, test=False, force_new=False, **kwargs):
        def features(tokens, index, history):
            word, pos = tokens[index]
            prev_word, prev_pos = tokens[index - 1] if index > 0 else ('START', 'START')
            next_word, next_pos = tokens[index + 1] if index + 1 < len(tokens) else ('END', 'END')

            next_next_word, next_next_pos = tokens[index + 2] if index + 2 < len(tokens) else ('END2', 'END2')
            prev_prev_word, prev_prev_pos = tokens[index - 2] if index > 1 else ('START2', 'START2')

            return {
                'word': word,
                'stem': SnowballStemmer("english").stem(word),
                'pos': pos,

                'next_word': next_word,
                'next_pos': next_pos,

                'two_words_ahead': next_next_word,
                'two_pos_ahead':next_next_pos,

                'prev_word': prev_word,
                'prev_pos': prev_pos,

                'two_words_past': prev_prev_word,
                'two_pos_past': prev_prev_pos,
            }
        if force_new or not os.path.isfile('cached_data/tagger.p'):
            # Default parameter described here rather in line so we can check file exists.
            try:
                data = conll2000.chunked_sents()
            except LookupError:
                sys.stderr.write('Warning: Default training data does not exist, downloading now...')
                sys.stderr.flush()
                nltk.download('conll2000')
                try:
                    data = conll2000.chunked_sents()
                except LookupError:
                    # If we fail a second time, then the download has failed.
                    sys.stderr.write('Error: Could not download training data.\nExiting.')
                    exit()
            data = list(data)
            # Randomize the order of the data
            random.shuffle(data)
            # Its a large corpus, so just 10% suffices.
            training_data = data[:int(.05*len(data))]

            training_data = [tree2conlltags(sent) for sent in training_data]
            training_data = [[((word, pos), chunk) for word, pos, chunk in sent] for sent in training_data]

            self.feature_detector = features
            self.tagger = ClassifierBasedTagger(
                train=training_data,
                feature_detector=features,
                **kwargs)

            # TODO: Find way to save classifier
            """
            with open('cached_data/tagger.p', 'wb') as output:
                pickle.dump(self.tagger, output, pickle.HIGHEST_PROTOCOL)
        else:
            with open('cached_data/tagger.p', 'rb') as input:
                self.tagger = pickle.load(input)
            """
        if test:
            test_data = data[int(.1*len(list(data))):]
            print(self.evaluate(test_data))

    def parse(self, sentence):
        """
        Processes a sentence, returning larger chunks.
        :param sentence: String to be analyzed
        :return: A list of tuples containing a word, it's tag, and its broader chunk.
        """
        chunks = self.tagger.tag(self.preprocess(sentence))
        chunks = conlltags2tree([(w, t, c) for ((w, t), c) in chunks])
        return chunks

    def preprocess(self, comment):
        """
        :param comment: A string
        :return: A list of pos_tagged sentences.
        """
        # Break into individual sentences.
        sentences = [nltk.tokenize.word_tokenize(sentence) for sentence in tokenizer.tokenize(comment)]
        # Apply basic POS tagging.
        try:
            tagged_sentences = [nltk.pos_tag(sentence) for sentence in sentences]
        except LookupError:
            nltk.download(nltk.download('averaged_perceptron_tagger'))
            tagged_sentences = [nltk.pos_tag(sentence) for sentence in sentences]

        return tagged_sentences

    def convert(self, tree):
        """
        Return a list of 3-tuples containing ``(word, tag, IOB-tag)``.
        Convert a tree to the CoNLL IOB tag format.

        :param tree: The tree to be converted.
        :type tree: Tree
        :rtype: list(tuple)
        """
        return tree2conlltags(tree)

    def get_nps(self, tags):
        """
        From the parsed tags, returns just the noun phrases, for possible entity linking.
        :param tags: A list containing tuples of word, tag, and chunk
        :return: A list of strings of the proper nouns
        """
        relevant_tags = [(t, i) for i, t in enumerate(tags) if 'NP' in t[2] and 'NNP' == t[1]]
        groups = []
        group = []
        last = -2
        for t, i in relevant_tags:
            if 'I' in t[2] or last+1 == i:
                group += [t]
                last = i
            else:
                groups.append(group)
                group = [t]
                last = i
        names = [' '.join([g[0] for g in group]) for group in groups[1:]]
        return names
