import time
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class TaggerTrainer(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, *args, **kwargs):
        print('[call] semanticaio.tagger.trainer.load')
        time.sleep(30)

    def save(self, *args, **kwargs):
        print('[call] semanticaio.tagger.trainer.save')
        time.sleep(5)

    @coroutine
    def train(self, *args, **kwargs):
        print('[event received] semanticaio.tagger.trainer.train')
        time.sleep(30)
        self.publish('semanticaio.tagger.trainer.trained')
        print('[emit] semanticaio.tagger.trainer.trained')

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.tagger.trainer.load')
        yield from self.register(self.save, 'semanticaio.tagger.trainer.save')
        yield from self.subscribe(self.train, 'semanticaio.tagger.trainer.train')
        print('[tagger-trainer started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(TaggerTrainer)
