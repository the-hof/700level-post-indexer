import sys
import re


class MarkovParser:
    SENTENCE_START_SYMBOL = '^'
    SENTENCE_END_SYMBOL = '$'

    def __init__(self, name, db, sentence_split_char='.', word_split_char=' '):
        self.name = name
        self.db = db
        self.sentence_split_char = sentence_split_char
        self.word_split_char = word_split_char
        self.whitespace_regex = re.compile('\s+')


    def parse(self, txt, author, depth):
        if txt is not None:
            sentences = txt.split(self.sentence_split_char)
            i = 0

            for sentence in sentences:
                sentence = self.whitespace_regex.sub(" ", sentence).strip()

                list_of_words = None
                if self.word_split_char:
                    list_of_words = sentence.split(self.word_split_char)
                else:
                    list_of_words = list(sentence.lower())

                words = [MarkovParser.SENTENCE_START_SYMBOL] * (depth - 1) \
                        + list_of_words \
                        + [MarkovParser.SENTENCE_END_SYMBOL] * (depth - 1)

                for n in range(0, len(words) - depth + 1):
                    self.db.add_words(author, "700level", words[n:n+depth])

                #self.db.commit()
                i += 1
                if i % 1000 == 0:
                    print i
                    sys.stdout.flush()