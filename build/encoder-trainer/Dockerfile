FROM semanticaio-python-base

WORKDIR /opt/service
ADD config ./config
ADD src/lib ./lib
ADD ./src/encoder-trainer/__init__.py ./__init__.py
ADD ./src/encoder-trainer/main.py ./main.py
CMD THEANO_FLAGS=mode=FAST_RUN,device=cpu,floatX=float32 python -u main.py
