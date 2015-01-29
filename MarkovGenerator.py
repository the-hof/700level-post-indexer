from random import randint

class MarkovGenerator:
    SENTENCE_START_SYMBOL = '^'
    SENTENCE_END_SYMBOL = '$'

    def __init__(self, db, sentence_split_char='.', word_split_char=' '):
        self.db = db
        self.sentence_split_char = sentence_split_char
        self.word_split_char = word_split_char

    def _get_next_word(self, author, project, word_list):
        chain = self.db.get_next_markov_chain(author, project, word_list)
        total_score = sum(chain.values())
        roll = randint(1, total_score)

        t = 0
        for w in chain.keys():
            t += chain[w]
            if roll <= t:
                return w

        return None

    def generate_sentence(self, author, project, depth):
        sentence = [MarkovGenerator.SENTENCE_START_SYMBOL] * (depth - 1)
        end_symbol = [MarkovGenerator.SENTENCE_END_SYMBOL] * (depth - 1)

        while True:
            tail = sentence[(-depth+1):]
            if tail == end_symbol:
                break
            word = self._get_next_word(author, project, tail)
            sentence.append(word)

        return self.word_split_char.join(sentence[depth-1:][:1-depth])
