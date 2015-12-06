import numpy as np
import h5py
from lib import data_util
from lib.codec import Codec
from lib.encoder_model import Model

config = data_util.get_config()
questions_path = config['path']['data']['questions']
encoded_path = config['path']['data']['encoded']
io_dim = Codec.n_chars
feature_dim = config['vectorDim']
seq_len = config['seqLength']
input_question = np.zeros((seq_len, io_dim), dtype = np.bool)
data_util.import_data()
dataset_size = data_util.count_lines(questions_path)

codec = Codec()
encoder = Model('encode')
try :
    encoder.load()
except :
    pass
encoder.compile()

with open(questions_path, 'r', encoding = 'utf-8') as questions_file, h5py.File(encoded_path, 'w') as encoded_file :
    encoded_dataset = encoded_file.create_dataset('data', (dataset_size, feature_dim), dtype = np.float32)
    for i, raw_question in enumerate(questions_file) :
        codec.encode(raw_question[:-1], input_question)
        encoded_dataset[i] = encoder.encode(input_question)
