import time
import asyncio
import numpy as np
from lib.codec import Codec
from lib.model import Model
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class EncoderTrainer(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch_size = 2
        self.needStop = False
        self.codec = Codec()
        self.model = Model('train')

    @asyncio.coroutine
    def train(self):
        self.publish('semanticaio.encoder.trainer.started')
        print('[emit] semanticaio.encoder.trainer.started')
        input_dataset = np.zeros((self.batch_size, self.codec.seq_len, self.codec.n_chars), dtype = np.bool)
        output_dataset = np.zeros((self.batch_size, self.codec.seq_len, self.codec.n_chars), dtype = np.bool)
        while not self.needStop :
            yield from asyncio.sleep(0.1)
            batch = yield from self.call('semanticaio.db.batch.get', size = self.batch_size)
            for i, question in enumerate(batch) :
                self.codec.encode(question['sentence'], input_dataset[i])
                if question['correctFormId'] == None :
                    self.codec.encode(question['sentence'], output_dataset[i])
                else :
                    correctQuestion = yield from self.call('semanticaio.db.get', id = question['correctFormId'])
                    self.codec.encode(correctQuestion['sentence'], output_dataset[i])
            (loss, accuracy) = self.model.train(input_dataset, output_dataset)
            print('training:', loss, accuracy)

        self.needStop = False
        self.publish('semanticaio.encoder.trainer.stopped')
        print('[emit] semanticaio.encoder.trainer.stopped')

    def load(self, *args, **kwargs):
        print('[call] semanticaio.encoder.trainer.load')
        try :
            self.model.load()
        except :
            print('[error] semanticaio.encoder.trainer.load')
        self.model.compile()

    def save(self, *args, **kwargs):
        print('[call] semanticaio.encoder.trainer.save')
        self.model.save()

    @asyncio.coroutine
    def start(self, *args, **kwargs):
        print('[event received] semanticaio.encoder.trainer.start')
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
