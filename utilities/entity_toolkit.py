# Collection of the frequently called functions we'll be using for entity linking

from wikidata.client import Client

import requests
import sys
import wikipedia


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

def political_party_to_value(party):
    '''
    :param party: A string representing the name of a political party
    :return: A value [-1.0, 1.0] representing this affiliation.
    '''
    # TODO: More nuanced approach, use wikipedia API rather than fixed values
    if 'republican' in party.lowercase():
        return 1
    elif 'democrat' in party.lowercase():
        return -1
    else:
        sys.stderr.write('ERROR: Method not yet completed.\n Cannot handle ' + party)
        return 0