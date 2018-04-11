# Collection of sentiment analysis tools to be used on this assignment, as well as event extraction tools to be used.

import nltk
import nltk.data
import nltk.tokenize

from nltk import ChunkParserI, ClassifierBasedTagger

from nltk.chunk import conlltags2tree, tree2conlltags
from nltk.corpus import conll2000
import random

import os
import pickle
import sys


class Tagger(ChunkParserI):
    def __init__(self, data=None, test=False, force_new=False, **kwargs):
        def features(tokens, index, _):
            word, pos = tokens[index]
            prev_word, prev_pos = tokens[index - 1] if index > 0 else ('START', 'START')
            next_word, next_pos = tokens[index + 1] if index + 1 < len(tokens) else ('END', 'END')

            return {
                'word': word,
                'pos': pos,

                'next-word': next_word,
                'next-pos': next_pos,

                'prev-word': prev_word,
                'prev-pos': prev_pos,
            }
        if force_new or not os.path.isfile('cached_data/tagger.p'):
            # Default parameter described here rather in line so we can check file exists.
            try:
                data = conll2000.chunked_sents()
            except LookupError:
                sys.stderr.write('Warning: Default training data does not exist, downloading now...')
                sys.stderr.flush()
                nltk.download(conll2000)
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
            training_data = data[:int(.1*len(data))]
            test_data = data[int(.1*len(data)):]

            training_data = [tree2conlltags(sent) for sent in training_data]
            training_data = [[((word, pos), chunk) for word, pos, chunk in sent] for sent in training_data]

            self.feature_detector = features
            self.tagger = ClassifierBasedTagger(
                train=training_data,
                feature_detector=features,
                **kwargs)

            # TODO: Find way to save classifier
            ''' 
            with open('cached_data/tagger.p', 'wb') as output:
                pickle.dump(self.tagger, output, pickle.HIGHEST_PROTOCOL)
        else:
            with open('cached_data/tagger.p', 'rb') as input:
                self.tagger = pickle.load(input)
            '''
        if test:
            print(self.evaluate(test_data))


    def parse(self, tagged_sent):
        chunks = self.tagger.tag(tagged_sent)

        # Transform the result from [((w1, t1), iob1), ...]
        # to the preferred list of triplets format [(w1, t1, iob1), ...]
        iob_triplets = [(w, t, c) for ((w, t), c) in chunks]

        # Transform the list of triplets to nltk.Tree format
        return conlltags2tree(iob_triplets)

# Load/generate requistie nltk files
try:
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
except LookupError:
    nltk.download('punkt')
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


def preprocess(comment):
    # Break into individual sentences.
    sentences = [nltk.tokenize.word_tokenize(sentence) for sentence in tokenizer.tokenize(comment)]
    # Apply basic POS tagging.
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in sentences]
    return tagged_sentences

# Just to be used in testing.
if __name__ == '__main__':
    comment = 'The news reported that Trump bombed Syria.'
    tagger = Tagger(test=True)
    print(tagger.parse(preprocess(comment)[0]))
