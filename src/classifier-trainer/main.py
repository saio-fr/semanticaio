import numpy as np
from lib.classifier_model import Model
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class ClassifierTrainer(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = Model()

    def load(self, *args, **kwargs):
        print('[call] semanticaio.classifier.trainer.load')
        try:
            self.model.load()
        except Exception as e:
            print('[error] semanticaio.classifier.trainer.load', e)

    def save(self, *args, **kwargs):
        print('[call] semanticaio.classifier.trainer.save')
        try:
            self.model.save()
        except Exception as e:
            print('[error] semanticaio.classifier.trainer.save', e)

    @coroutine
    def train(self, *args, **kwargs):
        print('[event received] semanticaio.classifier.trainer.train')
        try:
            self.model.train()
        except Exception as e:
            print('[error] semanticaio.classifier.trainer.train', e)
        self.publish('semanticaio.classifier.trainer.trained')
        print('[emit] semanticaio.classifier.trainer.trained')

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.classifier.trainer.load')
        yield from self.register(self.save, 'semanticaio.classifier.trainer.save')
        yield from self.subscribe(self.train, 'semanticaio.classifier.trainer.train')
        print('[classifier-trainer started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(ClassifierTrainer)
