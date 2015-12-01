FROM semanticaio-python-base

WORKDIR /opt/service
ADD ./src/classifier-trainer/main.py ./main.py
CMD THEANO_FLAGS=mode=FAST_RUN,device=cpu,floatX=float32 python -u main.py
