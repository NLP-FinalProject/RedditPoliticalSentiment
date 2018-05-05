# Collection of the frequently called functions we'll be using for entity linking

from bs4 import BeautifulSoup
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from wikidata.client import Client
from nltk.corpus import stopwords

import nltk.tokenize
import os
import re
import requests
import sys
import wikipedia
import urllib3
import json
from unidecode import unidecode
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

# Load/generate requisite nltk files
try:
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
except LookupError:
    nltk.download('punkt')
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

# more_stop_words = {'I', 'You', 'They', '\'s', 'everyone', 'us', 'we', 'He', 'boy', 'girl', 'child', 'son', 'daughter', 'kid', 'kids', 'we', 'mother', 'father', 'brother', 'sister', 'parent', 'parents', 'many', 'people', 'public', 'one', 'someone', 'people', 'families', 'person', 'citizen', 'citizens', 'individual', 'individuals', 'locals', 'team', 'teams', 'anyone', 'player', 'players'}
#
# stop_words = stop_words.union(more_stop_words)


stop_words_copy = set(stop_words)

for word in stop_words_copy:
    stop_words.add(word.lower())
    stop_words.add(word.capitalize())

class EntityLinker(object):
    def __init__(self, *, path='saved_data/entity_files/dict.json'):
        self.path = path

        # If file exists
        if os.path.isfile(path):
            # Load json file into dictionary
            self.load_dictionary()
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
        r = requests.post(serviceurl, data=payload)

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
            """
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
            """
        return taggedMentions

    def identify_all_entities(self, comments):
        """
        :param comments: A list of comments
        :return: A list of entities and events in the order they appear in the comment section, by each comment
        """
        combinedString = ""

        for i in comments:
            combinedString += ("-/:_START_OF_COMMENT_:/- " + unidecode(i[0]) + " -/:_END_OF_COMMENT_:/-")

        serviceurl = 'https://blender04.cs.rpi.edu/~jih/cgi-bin/ere.py'
        payload = {'textcontent': combinedString}
        r = requests.post(serviceurl, data=payload)

        parsed_html = BeautifulSoup(r.text, "html.parser")

        htmlString = str(parsed_html).replace('\n', ' ')

        commentList = (re.findall((r"-/:_START_OF_COMMENT_:/-(.*?)-/:_END_OF_COMMENT_:/-"), htmlString))

        taggedMentionsAllComments = []

        for i in commentList:
            parsed_html = BeautifulSoup(i, "html.parser")
            mentions = parsed_html.findAll('div')

            # Our list of entities and events
            taggedMentions = []

            for i in mentions:
                # If it is an entity like "George Bush"
                if (str(i).startswith("<div id=\"d")):
                    entityMention = re.sub("(.+Entity Mention: )|(<br/>.+)", "", str(i))
                    entityType = re.sub("(.+Entity Type: )|(<br/>.+)", "", str(i))
                    taggedMentions.append((entityMention, entityType))
            taggedMentionsAllComments.append(taggedMentions)
        return taggedMentionsAllComments

    def remove_unneeded_entities(self, entities):
        reduced_entities = []
        for commentEntityList in entities:
            reduced_entities.append([])
            for entity in commentEntityList:
                if(entity[0] not in stop_words and entity[1] == 'PER'):
                    reduced_entities[-1].append(entity)
        return reduced_entities

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
        try:
            resp = requests.get(url='https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&titles=' + title)
        except:
            return None
        data = resp.json()
        page_data = data['query']['pages'][list(data['query']['pages'].keys())[0]]
        try:
            page_properties = page_data['pageprops']
            item_id = page_properties['wikibase_item']
        except KeyError:
            return 'None found'

        # With item id in tow, extract political affiliation
        client = Client()
        entity = client.get(item_id, load=True)
        try:
            party_entity = entity.getlist(client.get('P102'))[0]
            return str(party_entity.label)
        except:
            return 'None found'

    def get_continuous_chunks(self, text):
        chunked = ne_chunk(pos_tag(word_tokenize(text)))
        continuous_chunk = []
        current_chunk = []

        for i in chunked:
            if type(i) == Tree:
                current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            elif current_chunk:
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
            else:
                continue

        if continuous_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)

        return continuous_chunk

    def entity_to_political_party(self, entity, type='Person', previous_subject_titles=[], train=True):
        """
        :param entity: String containing the name of the entity to be passed
        :return: A tuple containing the name of the matching page and that page's affiliation
        """
        # If already in dictionary, return dict entry instead of looking on Wikipedia
        if entity.lower() in self.ent_dict:
            try:
                if "None" in self.ent_dict[entity.lower()][1]:
                    return None
            except TypeError:
                # Strange glitch rarely encountered
                return None
            else:
                return self.ent_dict[entity.lower()]

        if train:
            try:
                pages = wikipedia.search(entity)
            except ConnectionError:
                return None
            # With the exception of Morrissey and Madonna, people have two words in their names
            if type =='Person':
                page_titles = [p.split() for p in pages]
                page_titles = [[w for w in title if '(' not in w] for title in page_titles]
                page_titles = [' '.join(title) for title in page_titles if len(title) >= 2]
            else:
                sys.stderr.write("ERROR: Only person entity-type supported")
                return None

            # Iterate through these titles
            for title in page_titles[:3]:
                found_party = self.page_title_to_political_party(title)
                if found_party != 'None found':
                    self.ent_dict[entity.lower()] = (title, found_party)
                    self.save_dictionary()
                    return title, found_party
            else:
                self.ent_dict[entity.lower()] = ('No political figure', 'None found')
                self.save_dictionary()
                return None
        else:
            return None

    def political_party_to_value(self, party):
        """
        :param party: A string representing the name of a political party
        :return: A value [-1.0, 1.0] representing this affiliation.
        """
        # TODO: More nuanced approach, use wikipedia API rather than fixed values
        if party is not None:
            if 'republican' in party.lower():
                return 1
            elif 'democrat' in party.lower():
                return -1

        return 0
