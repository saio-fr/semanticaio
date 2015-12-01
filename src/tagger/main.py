import time
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class Tagger(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, *args, **kwargs):
        print('[call] semanticaio.tagger.load')
        time.sleep(30)


    def tag(self, *args, **kwargs):
        print('[call] semanticaio.tagger.tag:', kwargs)
        time.sleep(3)
        result = {}
        result['tag0'] = True
        result['tag1'] = False
        result['tag2'] = True
        return result

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.tagger.load')
        yield from self.register(self.tag, 'semanticaio.tagger.tag')
        print('[tagger started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(Tagger)
