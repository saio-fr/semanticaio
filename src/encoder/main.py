import time
import random
import numpy as np
from lib.codec import Codec
from lib.model import Model
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class Encoder(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.codec = Codec()
        self.model = Model('encode')

    def load(self, *args, **kwargs):
        print('[call] semanticaio.encoder.load')
        try :
            self.model.load()
        except :
            print('[error] semanticaio.encoder.load')
        self.model.compile()

    def _encode(self, question) :
        coded_question = np.zeros((self.codec.seq_len, self.codec.n_chars), dtype = np.bool)
        self.codec.encode(question, coded_question)
        return self.model.encode(coded_question).tolist()

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
