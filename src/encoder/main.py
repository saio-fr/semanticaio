import time
import random
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class Encoder(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, *args, **kwargs):
        print('[call] semanticaio.encoder.load')
        time.sleep(30)


    def encode(self, *args, **kwargs):
        print('[call] semanticaio.encoder.encode:', kwargs)
        time.sleep(3)
        result = {}
        result['encoded'] = []
        if 'question' in kwargs :
            for char in kwargs['question']:
                result['encoded'].append(random.random())
            if 'decode' in kwargs and kwargs['decode'] :
                result['decoded'] = kwargs['question']
        elif 'questions' in kwargs :
            for question in kwargs['questions'] :
                encodedQuestion = []
                for char in question :
                    encodedQuestion.append(random.random())
                result['encoded'].append(encodedQuestion)
            if 'decode' in kwargs and kwargs['decode'] :
                result['decoded'] = kwargs['questions']
        return result

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.encoder.load')
        yield from self.register(self.encode, 'semanticaio.encoder.encode')
        print('[encoder started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(Encoder)
