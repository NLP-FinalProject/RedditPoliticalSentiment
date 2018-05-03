import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from keras.datasets import imdb
from tflearn.data_utils import to_categorical, pad_sequences

import tensorflow as tf
import tflearn
import os

# Load requisite datasets.
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

class SentimentClassifier(object):
    def __init__(self, *, load_path=None, save_path='saved_data/trained_models/model.tfl'):
        self.word_to_id = {k: v + 3 for k, v in imdb.get_word_index().items()}
        self.word_to_id["<PAD>"] = 0
        self.word_to_id["<START>"] = 1
        self.word_to_id["<UNK>"] = 2
        self.id_to_word = {v:k for k, v in self.word_to_id.items()}

        self.tokenizer = RegexpTokenizer(r'\w+')

        # Create model structure
        net = tflearn.input_data([None, 100])
        net = tflearn.embedding(net, input_dim=10000, output_dim=128)
        net = tflearn.lstm(net, 128, dropout=0.8)
        net = tflearn.fully_connected(net, 2, activation='softmax')
        net = tflearn.regression(net, optimizer='adam', learning_rate=0.0001, loss='categorical_crossentropy')
        self.model = tflearn.DNN(net, tensorboard_verbose=0)

        if load_path is None:
            self._train_model(save_path)
        else:
            self._load_model(load_path)

    def _train_model(self, save_path):
        '''
        :param save_path: Path to save the model to
        :return: None
        '''
        tf.reset_default_graph()
        train, test = imdb.load_data(num_words=10000, index_from=3)

        train_x, train_y = train
        test_x, test_y = test

        train_x = pad_sequences(train_x, maxlen=100, value=0.)
        test_x = pad_sequences(test_x, maxlen=100, value=0.)

        train_y = to_categorical(train_y, nb_classes=2)
        test_y = to_categorical(test_y, nb_classes=2)

        # Training
        self.model.fit(train_x, train_y, n_epoch=5, validation_set=(test_x, test_y), show_metric=True, batch_size=32)
        self.model.save(save_path)

    def _load_model(self, load_path):
        '''
        :param filename: .tfl file to be loaded.
        :return: None
        '''
        self.model.load(load_path)

    def predict(self, text, full_probs=False):
        '''
        :param text: Text to be classified.
        :param full_probs: If true, returns a list containing the negative probability and positive probability, if
                           false returns -1 if probably negative, 0 if unsure, or 1 if probably positive.
        :return: List or value, see above
        '''
        words = self.tokenizer.tokenize(text)
        vector = self.words_to_vector(words, max=10000)
        vector = pad_sequences([vector], maxlen=100, value=0.)
        probs = self.model.predict(vector)[0].tolist()
        if full_probs:
            return probs
        else:
            pos, neg = probs
            if abs(pos-neg) < 0.1:
                return 0
            else:
                return 2*probs.index(max(probs))-1

    def check_conversion(self, text):
        """
        TODO: REMOVE BEFORE FINAL RELEASE
        This is a function used just to check that the conversion of words to vectors is being done correctly.
        :param text: Text to be evaluated
        :return: A string representing the conversion of this text to tokens, tokens to vector, and vector back to text.
        """
        words = self.tokenizer.tokenize(text)
        vector = self.words_to_vector(words)
        return vector, self.vector_to_words(vector)

    def vector_to_words(self, vector):
        '''
        :param vector: Vector of numbers corresponding to words in the dictionary used in the given corpus
        :return: A string containing all the words corresponding to the numbers in the vector.
        '''
        return ' '.join(self.id_to_word[i] for i in vector)

    def words_to_vector(self, words, max):
        '''
        :param words: A string containing, presumably, multiple words.
        :return: A list of integers starting with 0.
        '''
        words[0] = words[0].lower()
        words = [word for word in words if word.lower() not in stop_words]
        vector = [1] + [self.word_to_id[word] if word in self.word_to_id and self.word_to_id[word] <= max else 2 for word in words]
        return vector


if __name__ == '__main__':
    # If run individually, we build the classifier.
    classifier = SentimentClassifier(save_path='trained_models/model.tfl')
    print("Testing positive response.")
    print(classifier.predict("I love tflearn more than anything! I want to use it every day!"))
    print(classifier.predict("I think that tflearn is the worst thing I have ever seen."))
    test_phrase = "I heard on the news today that the president Trump is responsible for the destruction of Hawaii."
    print("Testing phrase vectorization")
    vector, conv = classifier.check_conversion(test_phrase)
    print("Generated vector: " + str(vector))
    print("Coverted to plaintext: " + conv)