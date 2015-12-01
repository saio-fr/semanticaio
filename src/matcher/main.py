import time
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class Matcher(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, *args, **kwargs):
        print('[call] semanticaio.matcher.load')
        time.sleep(30)


    def match(self, *args, **kwargs):
        print('[call] semanticaio.matcher.match:', kwargs)
        time.sleep(3)
        result = {}
        result['id'] = 2
        result['distance'] = 0.042
        return result

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.matcher.load')
        yield from self.register(self.match, 'semanticaio.matcher.match')
        print('[matcher started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(Matcher)
