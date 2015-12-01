import time
import asyncio
from concurrent.futures import ProcessPoolExecutor
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class EncoderTrainer(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.needStop = False

    @asyncio.coroutine
    def _train(self):
        while not self.needStop :
            batch = yield from self.call('semanticaio.db.batch.get', size = 2)
            print('batch', batch)
            time.sleep(21)
            print('training...')
            yield from asyncio.sleep(0.1)
        self.needStop = False

    @asyncio.coroutine
    def train(self):
        self.publish('semanticaio.encoder.trainer.started')
        print('[emit] semanticaio.encoder.trainer.started')
        #yield from asyncio.get_event_loop().run_in_executor(ProcessPoolExecutor(), self._train)
        yield from self._train()
        self.publish('semanticaio.encoder.trainer.stopped')
        print('[emit] semanticaio.encoder.trainer.stopped')

    def load(self, *args, **kwargs):
        print('[call] semanticaio.encoder.trainer.load')
        time.sleep(5)

    def save(self, *args, **kwargs):
        print('[call] semanticaio.encoder.trainer.save')
        time.sleep(5)

    @asyncio.coroutine
    def start(self, *args, **kwargs):
        print('[event received] semanticaio.encoder.trainer.start')
        time.sleep(2)
        yield from self.train()

    def stop(self, *args, **kwargs):
        print('[event received] semanticaio.encoder.trainer.stop')
        self.needStop = True

    @asyncio.coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.encoder.trainer.load')
        yield from self.register(self.save, 'semanticaio.encoder.trainer.save')
        yield from self.subscribe(self.start, 'semanticaio.encoder.trainer.start')
        yield from self.subscribe(self.stop, 'semanticaio.encoder.trainer.stop')
        print('[encoder-trainer started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(EncoderTrainer)
