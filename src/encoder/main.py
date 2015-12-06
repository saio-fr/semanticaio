import numpy as np
import h5py
from lib import data_util
from lib.codec import Codec
from lib.encoder_model import Model
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class Encoder(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.semantic_config = data_util.get_config()
        self.codec = Codec()
        self.model = Model('encode')

    def load(self, *args, **kwargs):
        print('[call] semanticaio.encoder.load')
        try :
            self.model.load()
        except :
            print('[error] semanticaio.encoder.load')
        self.model.compile()

        # encode all questions
        questions_path = self.semantic_config['path']['data']['questions']
        encoded_path = self.semantic_config['path']['data']['encoded']
        feature_dim = self.semantic_config['vectorDim']
        dataset_size = data_util.count_lines(questions_path)
        with open(questions_path, 'r', encoding = 'utf-8') as questions_file, h5py.File(encoded_path, 'w') as encoded_file :
            encoded_dataset = encoded_file.create_dataset('data', (dataset_size, feature_dim), dtype = np.float32)
            for i, question in enumerate(questions_file) :
                encoded_dataset[i] = self._encode(question[:-1], np_return = True)

    def _encode(self, question, np_return = False) :
        coded_question = np.zeros((self.codec.seq_len, self.codec.n_chars), dtype = np.bool)
        self.codec.encode(question, coded_question)
        encoded = self.model.encode(coded_question)
        if np_return :
            return encoded
        return encoded.tolist()

    def encode(self, *args, **kwargs):
        print('[call] semanticaio.encoder.encode:', kwargs)
        result = {}
        if 'question' in kwargs :
            result['encoded'] = self._encode(kwargs['question'])
        elif 'questions' in kwargs :
            result['encoded'] = []
            for question in kwargs['questions'] :
                result['encoded'].append(self._encode(question))
        return result

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.encoder.load')
        yield from self.register(self.encode, 'semanticaio.encoder.encode')
        print('[encoder started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(Encoder)
