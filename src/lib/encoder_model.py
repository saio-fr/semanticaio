import sys
sys.setrecursionlimit(100000)
import numpy as np
import h5py
from .data_util import get_config
from .codec import Codec
from keras.models import Sequential as SeqModel
from keras.layers.core import RepeatVector, TimeDistributedDense
from keras.layers.recurrent import GRU, SimpleRNN
from keras.layers.containers import Sequential as SeqContainer
from keras.optimizers import Adadelta

class Model() :

    # mode = 'encode' || 'train'
    def __init__(self, mode) :
        self.io_dim = Codec.n_chars
        semantic_config = get_config()
        self.feature_dim = semantic_config['vectorDim']
        self.seq_len = semantic_config['seqLength']
        self.encoder_path = semantic_config['path']['model']['encoder']
        self.decoder_path = semantic_config['path']['model']['decoder']
        self.mode = mode
        self.model = SeqModel()
        self.encoder = SeqContainer()
        self.encoder.add(TimeDistributedDense(
            input_dim = self.io_dim,
            input_length = self.seq_len,
            output_dim = self.feature_dim,
            activation = 'sigmoid'))
        self.encoder.add(GRU(
            input_dim = self.feature_dim,
            input_length = self.seq_len,
            output_dim = self.feature_dim,
            activation = 'sigmoid',
            inner_activation = 'hard_sigmoid',
            return_sequences = True))
        self.encoder.add(GRU(
            input_dim = self.feature_dim,
            input_length = self.seq_len,
            output_dim = self.feature_dim,
            activation = 'sigmoid',
            inner_activation = 'hard_sigmoid',
            return_sequences = False))
        self.model.add(self.encoder)
        if mode == 'train' :
            self.decoder = SeqContainer()
            self.decoder.add(SimpleRNN(
                input_dim = self.feature_dim,
                input_length = self.seq_len,
                output_dim = self.feature_dim,
                activation = 'sigmoid',
                return_sequences = True))
            self.decoder.add(TimeDistributedDense(
                input_dim = self.feature_dim,
                input_length = self.seq_len,
                output_dim = self.io_dim,
                activation = 'sigmoid'))
            self.model.add(RepeatVector(self.seq_len, input_shape = (self.feature_dim,)))
            self.model.add(self.decoder)

    def _load_weights(self, path) :
        with h5py.File(path, 'r') as file :
            n_layers = file.attrs.get('n_layers')[0]
            weights = []
            for i in range(n_layers) :
                layer_weights = file['/layer_' + str(i)][()]
                weights.append(layer_weights)
            return weights

    def load(self) :
        encoder_weights = self._load_weights(self.encoder_path)
        self.encoder.set_weights(encoder_weights)
        if self.mode == 'train' :
            decoder_weights = self._load_weights(self.decoder_path)
            self.decoder.set_weights(decoder_weights)

    def _save_weights(self, weights, path) :
        with h5py.File(path, 'w') as file :
            n_layers = len(weights)
            file.attrs.create('n_layers', np.array([n_layers]))
            for i, layer_weights in enumerate(weights) :
                file.create_dataset('layer_' + str(i), data = layer_weights)

    def save(self) :
        if self.mode != 'train' :
            raise ValueError('invalid mode')
        encoder_weights = self.encoder.get_weights()
        decoder_weights = self.decoder.get_weights()
        self._save_weights(encoder_weights, self.encoder_path)
        self._save_weights(decoder_weights, self.decoder_path)

    def compile(self) :
        self.model.compile(loss = 'categorical_crossentropy', optimizer = Adadelta(clipnorm = 1.))

    # in_data & out_data numpy bool array of shape (n_sample, seq_len, io_dim)
    # return train (loss, accuracy)
    def train(self, in_data, out_data) :
        if self.mode != 'train' :
            raise ValueError('invalid mode')
        return self.model.train_on_batch(in_data, out_data, accuracy = True)

    # in_data & out_data numpy bool array of shape (n_sample, seq_len, io_dim)
    # return the evaluation (loss, accuracy)
    def evaluate(self, in_data, out_data) :
        if self.mode != 'train' :
            raise ValueError('invalid mode')
        return self.model.test_on_batch(in_data, out_data, accuracy = True)

    # sequence : numpy bool array of shape (seq_len, io_dim)
    # return : numpy float32 array of shape (feature_dim)
    def encode(self, sequence) :
        if self.mode != 'encode' :
            raise ValueError('invalid mode')
        input_sequences = np.ndarray((1, self.seq_len, self.io_dim), dtype = np.bool)
        input_sequences[0] = sequence
        return self.model.predict(input_sequences)[0]
