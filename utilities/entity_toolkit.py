# Collection of the frequently called functions we'll be using for entity linking

from wikidata.client import Client

import requests
import sys
import wikipedia
from bs4 import BeautifulSoup
import re
requests.packages.urllib3.disable_warnings()

def identify_entity(sentence):
    '''
    :param sentence:
    :return: A list of entities and events in the order they appear in the sentence
    '''
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

def page_title_to_political_party(title):
    '''
    :param wiki: a valid WikipediaPage object
    :return: A string representing the political party or affiliation of the entity described in the wikipage, if
            available. Otherwise, a string 'None' is returned.
    '''
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

def entity_to_political_party(entity, type='Person', previous_subject_titles=[]):
    '''
    :param entity: String containing the name of the entity to be passed
    :return: A tuple containing the name of the matching page and that page's affiliation
    '''
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
        found_party = page_title_to_political_party(title)
        if found_party != 'None found':
            return title, found_party
    return 'No political figure', 'None found'
