# Examples of the ways in which the various toolkits can be used

import utilities.entity_toolkit as et
import utilities.reddit_toolkit as rt

print("Easily identifiable figures")
figures = ['Donald Trump', 'Barack Obama', 'Abraham Lincoln', 'Jill Stein', 'Adolf Hitler', 'Nathan Potolsky']
for figure in figures:
    result = et.entity_to_political_party(figure)
    print(result[0] + ': ' + result[1])


print("\nIncomplete names")
figures = ['Obama', 'Trump', 'Lincoln', 'Stein', 'Hitler', 'Potolsky']
for figure in figures:
    result = et.entity_to_political_party(figure)
    print(figure + ' -> ' + result[0] + ': ' + result[1])