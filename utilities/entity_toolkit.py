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


    def identify_entity(self, sentence):
        """
        :param sentence:
        :return: A list of entities and events in the order they appear in the sentence
        """
        service_url = 'https://blender04.cs.rpi.edu/~jih/cgi-bin/ere.py'
        payload = {'textcontent': sentence}
        r = requests.post(service_url, data=payload)

        parsed_html = BeautifulSoup(r.text, "html.parser")
        # We are only concerned about the div lines as that's where the entities and events are in the HTML
        mentions = parsed_html.findAll('div')

        # Our list of entities and events
        tagged_mentions = []

        # For each mention in sentence
        for i in mentions:
            # If it is an entity like "George Bush"
            if (str(i).startswith("<div id=\"d")):
                entity_id = re.sub("(.+Entity ID: )|(<br/>.+)", "", str(i))
                entity_mention = re.sub("(.+Entity Mention: )|(<br/>.+)", "", str(i))
                entity_mention_type = re.sub("(.+Entity Mention Type: )|(<br/>.+)", "", str(i))
                entity_type = re.sub("(.+Entity Type: )|(<br/>.+)", "", str(i))
                entity_class = re.sub("(.+Entity Class: )|(<br/>.+)", "", str(i))
                tagged_mentions.append(['Entity', entity_id, entity_mention, entity_mention_type, entity_type,
                                        entity_class])
        return tagged_mentions

    def identify_all_entities(self, comments, filter=True):
        """
        :param comments: A list of comments
        :return: A list of entities and events in the order they appear in the comment section, by each comment
        """
        combined_string = ""
        for comment_body, _ in comments:
            combined_string += "-/:_START_OF_COMMENT_:/- " + unidecode(comment_body) + " -/:_END_OF_COMMENT_:/-"

        service_url = 'https://blender04.cs.rpi.edu/~jih/cgi-bin/ere.py'
        payload = {'textcontent': combined_string}
        r = requests.post(service_url, data=payload)

        parsed_html = BeautifulSoup(r.text, "html.parser")

        html_string = str(parsed_html).replace('\n', ' ')

        comment_list = (re.findall(r"-/:_START_OF_COMMENT_:/-(.*?)-/:_END_OF_COMMENT_:/-", html_string))

        tagged_mentions_all_comments = []

        for comment in comment_list:
            parsed_html = BeautifulSoup(comment, "html.parser")
            mentions = parsed_html.findAll('div')

            # Our list of entities and events
            taggged_mentions = []

            # For each raw entity (still in html) in list
            for entity_html in mentions:
                # If it is an entity like "George Bush", parse out the entity and type
                if (str(entity_html).startswith("<div id=\"d")):
                    entity_mention = re.sub("(.+Entity Mention: )|(<br/>.+)", "", str(entity_html))
                    entity_type = re.sub("(.+Entity Type: )|(<br/>.+)", "", str(entity_html))
                    taggged_mentions.append((entity_mention, entity_type))
            tagged_mentions_all_comments.append(taggged_mentions)
        return tagged_mentions_all_comments

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

    def entity_to_political_party(self, *, entity, ent_type='PER', previous_subject_titles=[], train=True):
        """
        :param entity: String containing the name of the entity to be passed
        :return: A tuple containing the name of the matching page and that page's affiliation
        """
        # If already in dictionary, return dict entry instead of looking on Wikipedia
        if entity.lower() in self.ent_dict:
            try:
                if "None" in self.ent_dict[entity.lower()][1]:
                    return None
                else:
                    return self.ent_dict[entity.lower()]
            except TypeError:
                return None

        if train:
            try:
                pages = wikipedia.search(entity)
            except ConnectionError:
                return None
            # With the exception of Morrissey and Madonna, people have two words in their names
            if ent_type == 'PER':
                page_titles = [p.split() for p in pages]
                page_titles = [[w for w in title if '(' not in w] for title in page_titles]
                page_titles = [' '.join(title) for title in page_titles if len(title) >= 2]
            else:
                # TODO: ADD SUPPORT TYPES FOR NON-PERSON ENTITIES
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
