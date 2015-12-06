import numpy as np
import h5py
from lib.data_util import get_config, FileLineReader
from scipy.spatial.distance import sqeuclidean as dist
from asyncio import coroutine
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

class Matcher(ApplicationSession):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.semantic_config = get_config()
        self.feature_dim = self.semantic_config['vectorDim']

    def load(self, *args, **kwargs):
        print('[call] semanticaio.matcher.load')
        self.raw_questions_reader = FileLineReader(self.semantic_config['path']['data']['questions'])
        self.raw_questions_reader.close()
        with h5py.File(self.semantic_config['path']['data']['encoded']) as encoded_file :
            self.encoded_questions = np.array(encoded_file['/data'][()], dtype = np.float32)


    def match(self, *args, **kwargs):
        print('[call] semanticaio.matcher.match:', kwargs)
        input_question = np.array(kwargs['question'], dtype = np.float32)
        result = {}
        distances = list(map(lambda x: dist(x, input_question), self.encoded_questions))
        result['id'] = int(np.argmin(distances))
        result['distance'] = float(distances[result['id']])
        self.raw_questions_reader.open()
        result['question'] = self.raw_questions_reader.readline(result['id'])
        self.raw_questions_reader.close()
        return result

    @coroutine
    def onJoin(self, details):
        yield from self.register(self.load, 'semanticaio.matcher.load')
        yield from self.register(self.match, 'semanticaio.matcher.match')
        print('[matcher started]')

ApplicationRunner(url = 'ws://crossbar:8080', realm = 'semanticaio').run(Matcher)
