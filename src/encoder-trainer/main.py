import asyncio
import numpy as np
from lib import data_util
from lib.codec import Codec
from lib.encoder_model import Model
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class EncoderTrainer(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.semantic_config = data_util.get_config()
        self.batch_size = self.semantic_config['trainBatchSize']
        self.needStop = False
        self.codec = Codec()
        self.model = Model('train')

    @asyncio.coroutine
    def train(self, pretrain):
        self.publish('semanticaio.encoder.trainer.started')
        print('[emit] semanticaio.encoder.trainer.started')
        yield from asyncio.sleep(0.1)
        data_path = ''
        if pretrain :
            data_path = self.semantic_config['path']['data']['pretrainSelectedQuestions']
        else :
            data_path = self.semantic_config['path']['data']['questions']

        while True :
            for batch in data_util.batch_read(data_path, self.batch_size, randomize = True) :
                dataset = np.zeros((len(batch), self.codec.seq_len, self.codec.n_chars), dtype = np.bool)
                for i, question in enumerate(batch) :
                    self.codec.encode(question, dataset[i])
                (loss, accuracy) = self.model.train(dataset, dataset)
                print('training:', loss, accuracy)
                yield from asyncio.sleep(0.1)
                if self.needStop :
                    self.needStop = False
                    self.publish('semanticaio.encoder.trainer.stopped')
                    print('[emit] semanticaio.encoder.trainer.stopped')
                    return

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
        pretrain = 'pretrain' in kwargs and kwargs['pretrain']
        yield from self.train(pretrain)

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
