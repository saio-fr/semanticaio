from lib.classifier_model import Model
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class Classifier(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = Model()

    def load(self, *args, **kwargs):
        print('[call] semanticaio.classifier.load')
        try:
            self.model.load()
        except Exception as e:
            print('[error] semanticaio.classifier.load', e)

    def classify(self, *args, **kwargs):
        print('[call] semanticaio.classifier.classify:', kwargs)
        try:
            result = {}
            result['class'] = self.model.predict(kwargs['question'])
            return result
        except Exception as e:
            print('[error] semanticaio.classifier.classify', e)

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.classifier.load')
        yield from self.register(self.classify, 'semanticaio.classifier.classify')
        print('[classifier started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(Classifier)
