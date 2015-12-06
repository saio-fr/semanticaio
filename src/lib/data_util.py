import random
import codecs
import json
import csv
import h5py
import numpy as np

def get_config() :
    with open('config/semantic.json', 'r', encoding = 'utf-8') as config_file :
        return json.load(config_file)

def count_lines(path) :
    with open(path, 'r', encoding = 'utf-8') as file :
        return sum(1 for line in file)

# read questions.csv & write questions.txt & classes.hdf5
# then read pretrainQuestions and select those shorter than seqLenght
def import_data() :
    config = get_config()
    csv_path = config['path']['data']['csv']
    questions_path = config['path']['data']['questions']
    pretrain_questions_path = config['path']['data']['pretrainQuestions']
    pretrain_selected_questions_path = config['path']['data']['pretrainSelectedQuestions']
    classes_path = config['path']['data']['classes']
    classes = config['classes']
    max_question_len = config['seqLength']
    class_indexes = []

    # import questions & classes
    with open(csv_path, 'r', newline = '', encoding = 'utf-8') as csv_file, open(questions_path, 'w', encoding = 'utf-8') as questions_file :
        def hack_read(file) :
            for line in file :
                yield line
        csv_reader = csv.reader(hack_read(csv_file), dialect = 'excel', delimiter = ',', quotechar = '"')
        first_line = True
        for row in csv_reader :
            if first_line :
                first_line = False
                continue
            question = row[0] + '\n'
            label = -1
            try :
                if len(question) > max_question_len + 1 :
                    raise ValueError('max question length exceeded')
                label = classes.index(row[1])
            except Exception as e:
                print('[error] import: id:', len(class_indexes), e)
                continue
            questions_file.write(question)
            class_indexes.append(label)
    with h5py.File(classes_path, 'w') as classes_file :
        classes_file.create_dataset('data', data = class_indexes)

    # select short questions from pretrain dataset
    with open(pretrain_questions_path, 'r', encoding = 'utf-8') as input_pretrain_file :
        with open(pretrain_selected_questions_path, 'w', encoding = 'utf-8') as output_pretrain_file :
            for line in input_pretrain_file :
                if len(line) - 1 <= max_question_len :
                    output_pretrain_file.write(line)

class FileLineReader() :
    def __init__(self, path) :
        self.path = path
        self.n_lines = count_lines(path)
        self.file = open(path, 'rb')
        self.closed = False
        self.line_offset = np.zeros((self.n_lines,), dtype = np.int32)
        offset_count = 0
        for i, line in enumerate(self.file) :
            self.line_offset[i] = offset_count
            offset_count += len(line)

    # does not return line break
    def readline(self, n) :
        if self.closed :
            raise ValueError('file closed')
        if  n < 0 or n >= self.n_lines :
            raise ValueError('line index out of file')
        self.file.seek(self.line_offset[n])
        return self.file.readline().decode('utf-8')[:-1]

    def open(self):
        self.file = open(self.path, 'rb')
        self.closed = False

    def close(self) :
        self.file.close()
        self.closed = True

# return generator([string])
def batch_read(path, batch_size, randomize = False) :
    reader = FileLineReader(path)
    n_lines = reader.n_lines
    indexes = list(range(n_lines))
    if randomize :
        random.shuffle(indexes)
    partition_index = 0
    while batch_size * partition_index < n_lines :
        partition_start = partition_index * batch_size
        partition_end = min(partition_start + batch_size, n_lines)
        partition = list(map(reader.readline, indexes[partition_start:partition_end]))
        yield partition
        partition_index += 1
    reader.close()
