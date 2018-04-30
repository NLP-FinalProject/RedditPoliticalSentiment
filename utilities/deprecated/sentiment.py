
# APPROACH 1

class SentimentClassifier():
    # Used to map NLTK type to sentiment database types
    nltk_map = {
        'NN': 'noun',
        'JJ': 'adj',
        'RB': 'adverb',
        'VB': 'verb',
    }

    def __int__(self, sentiment_file="sentiment_files/list.tff"):
        self.load_sentiments(sentiment_file)

    def load_sentiments(self, sentiment_file):
        """
        :param sentiment_file: The file containing a list of the words used to assess sentiment.
        :return: A dictionary containing a link from each word to the Sentiment object. In the core of this assignment
                 only the polarity of this sentiment will be used, but we're linking to the whole object rather than
                 the sentiment exclusively since it allows some variations to be applied based on a variety of variables
                 at a later point, if desired.
        """
        if not os.path.isfile(sentiment_file):
            sys.stderr.write("ERROR: Sentiment file " + sentiment_file + " does not exist.")
            exit(1)

        with open(sentiment_file) as file:
            lines = file.readlines()
        lines = [line.strip() for line in lines]

        self.sentiments = {}
        Sentiment = namedtuple('Sentiment', 'type word pos stemmed polarity')

        for line in lines:
            vars = line.split(' ')
            type = vars[0][vars[0].index('=') + 1:]
            word = vars[2][vars[2].index('=') + 1:]
            pos = vars[3][vars[3].index('=') + 1:]
            stemmed = True if vars[4][vars[4].index('=') + 1:][0] == 'y' else False
            # Two lines in the file, 5500 and 5501, have vars[5] = 'm' for some unknown reason. This is to avoid those.
            if vars[5] == 'm':
                priorpolarity = vars[6][vars[6].index('=') + 1:]
            else:
                priorpolarity = vars[5][vars[5].index('=') + 1:]
            self.sentiments[(word, pos)] = Sentiment(type, word, pos, stemmed, priorpolarity)
        if len(self.sentiments.items()) == 0:
            sys.stderr('ERROR: No lines could be read in the linked file, although the file does exist.')
            exit(2)

    def tally_word_sentiments(review, sentiment_dictionary):
        """
        The most basic sentiment analysis to meet the requirements of this small assignment.
        :param paragraph: String to be reviewed.
        :return: A tuple containing the number of positive classified words, number of negative classified words, and total.
        """
        # In this simple version, we don't care about the different sentences or anything, so just make a list of words.
        words = review.split(' ')

        # Used to map NLTK type to sentiment database types
        nltk_map = {
            'NN': 'noun',
            'JJ': 'adj',
            'RB': 'adverb',
            'VB': 'verb',
        }

        # If mistakenly passed an empty string, return 0s and avoid this upcoming computation
        if len(words) == 0:
            return 0, 0, 0

        # Fix numbers, which had no match in the dictionary.
        words = [w for w in words if not any(c.isdigit() for c in w)]
        # remove punctuation, and make lowercase for better dictionary integration
        for i, word in enumerate(words):
            words[i] = ''.join([c for c in word if c not in set(string.punctuation)]).lower()

        words = [w for w in words if len(w) > 0]
        posts = [nltk_map[t[1]] if t[1] in nltk_map.keys() else 'anypos' for t in nltk.pos_tag(words)]

        # Make pairs for the discovered types, but of course override the pos with 'anypos' if the sentiment lexicon
        # doesn't care about the position.
        word_pos_pair = [(word, pos) if (word, 'anypos') not in sentiment_dictionary else (word, 'anypos')
                         for word, pos in zip(words, posts)]

        print([pair for pair in word_pos_pair if pair in sentiment_dictionary and
               sentiment_dictionary[pair].polarity == 'positive'])
        positive_count = len([pair for pair in word_pos_pair if pair in sentiment_dictionary and
                              sentiment_dictionary[pair].polarity == 'positive'])
        negative_count = len([pair for pair in word_pos_pair if pair in sentiment_dictionary and
                              sentiment_dictionary[pair].polarity == 'negative'])
        total = len(words)

        return positive_count, negative_count, total

# APPROACH 2

class SentimentClassifier():

    def __init__(self, lexicon_path="sentiment_files/lexicon.tsv"):
        self.lexicon_dictionary = {}
        file = open(lexicon_path, "r")
        for line in file:
            split_line = line.split()
            self.lexicon_dictionary[split_line[0]] = float(split_line[1])

    def get_sentiments(self, word_list):
        word_sentiment_list = []
        for word in word_list:
            cur_word = word[0]
            normalized_word = cur_word.lower()
            # If last character is not a letter ("Good!" to "good")
            if(normalized_word[-1].isalpha() is False):
                normalized_word = normalized_word[:-1]  # Strip last character

            # If word is not in dictionary, change normalized_word to stemmed version (ie, "absurdly" to "absurd")
            sentiment = self.lexicon_dictionary.get(normalized_word)
            if(sentiment is None):
                normalized_word = SnowballStemmer("english").stem(normalized_word)
            sentiment = self.lexicon_dictionary.get(normalized_word)
            if (sentiment is None):
                sentiment = 0

            word_sentiment = (cur_word , sentiment)
            print(word_sentiment)
            word_sentiment_list.append(word_sentiment)
        return word_sentiment_list

    def get_comment_sentiment(self, word_sentiment_list):
        overall_sentiment = 0
        nonzero_sentiment_word_count = 0
        for entry in word_sentiment_list:
            if (entry[1] is not 0):
                overall_sentiment += entry[1]
                nonzero_sentiment_word_count += 1
        return (overall_sentiment/nonzero_sentiment_word_count)

    def get_overall_comment_section_sentiment(self, comment_sentiment_list):
        overall_sentiment = 0
        comment_count = 0
        for entry in comment_sentiment_list:
            overall_sentiment += self.get_comment_sentiment(entry)
            comment_count += 1
        return (overall_sentiment/comment_count)