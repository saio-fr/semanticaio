import h5py
import numpy as np
from .data_util import get_config
from sklearn.externals import joblib
from sklearn.svm import SVC

class Model() :

    def __init__(self) :
        self.config = get_config()
        self.class_labels = self.config['classes']
        self.model = SVC(decision_function_shape = 'ovr')
        self.ready = False

    # can throw
    def load(self) :
        model_path = self.config['path']['model']['classifier']
        self.model = joblib.load(model_path)
        self.ready = True

    # can throw
    def save(self) :
        if not self.ready :
            raise ValueError('classifier not trained nor loaded from disk')
        model_path = self.config['path']['model']['classifier']
        joblib.dump(self.model, model_path)

    def train(self) :
        questions_path = self.config['path']['data']['encoded']
        classes_path = self.config['path']['data']['classes']
        with h5py.File(questions_path, 'r') as questions_file, h5py.File(classes_path, 'r') as classes_file :
            questions = np.array(questions_file['/data'][()], dtype = np.float32)
            classes = np.array(classes_file['/data'][()], dtype = np.int16)
            self.model.fit(questions, classes)
        self.ready = True

    def predict(self, questionVector):
        if not self.ready :
            raise ValueError('classifier not trained nor loaded from disk')
        class_id = self.model.predict([questionVector])
        return self.class_labels[class_id]
