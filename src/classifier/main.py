import time
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class Classifier(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(*args, **kwargs):
        print('[call] semanticaio.classifier.load')
        time.sleep(30)

    def classify(*args, **kwargs):
        print('[call] semanticaio.classifier.classify:', kwargs)
        time.sleep(3)
        result = {}
        result['class0'] = 'label0'
        result['class1'] = 'label1'
        return result

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.classifier.load')
        yield from self.register(self.classify, 'semanticaio.classifier.classify')
        print('[classifier started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(Classifier)
