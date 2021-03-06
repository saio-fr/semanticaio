import time
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class ClassifierTrainer(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, *args, **kwargs):
        print('[call] semanticaio.classifier.trainer.load')
        time.sleep(30)

    def save(self, *args, **kwargs):
        print('[call] semanticaio.classifier.trainer.save')
        time.sleep(5)

    @coroutine
    def train(self, *args, **kwargs):
        print('[event received] semanticaio.classifier.trainer.train')
        time.sleep(30)
        self.publish('semanticaio.classifier.trainer.trained')
        print('[emit] semanticaio.classifier.trainer.trained')

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.classifier.trainer.load')
        yield from self.register(self.save, 'semanticaio.classifier.trainer.save')
        yield from self.subscribe(self.train, 'semanticaio.classifier.trainer.train')
        print('[classifier-trainer started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(ClassifierTrainer)
