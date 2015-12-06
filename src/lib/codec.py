import numpy as np
from .data_util import get_config

# encoding:
# - [1, 99 (n_chars - 2)]: known chars
# - 0: '~' ie unknown char
class Codec():
    n_chars = 100

    def __init__(self):
        chars = 'AaàâBbCcçDdEeéèêëFfGgHhIiîïJjKkLlMmNnOoôPpQqRrSsTtUuùûüVvWwXxYyZz0123456789 ,.?():;!&-+*/\\_"\'#@%€$£'
        self.n_chars = Codec.n_chars
        self.seq_len = get_config()['seqLength']
        self.char_index = dict((c, i + 1) for i, c in enumerate(chars))
        self.index_char = dict((i + 1, c) for i, c in enumerate(chars))

    def _get_index(self, char):
        if char in self.char_index :
            return self.char_index[char]
        return 0

    def _encode_index(self, index, out):
        for i in range(self.n_chars) :
            out[i] = (i == index)

    def encode(self, sentence, out):
        for i in range(min(self.seq_len, len(sentence))) :
            self._encode_index(self._get_index(sentence[i]), out[i])
        for i in range(len(sentence), self.seq_len) :
            self._encode_index(-1, out[i])

    def _get_char(self, vec) :
        i = np.argmax(vec)
        confidence = np.max(vec)
        if confidence < 0.5 :
            return None
        if i == 0 :
            return '~'
        return self.index_char[i]

    def decode(self, tensor) :
        res = ''
        char = ''
        for i in range(self.seq_len) :
            char = self._get_char(tensor[i])
            if char is None :
                break
            res += char
        return res
