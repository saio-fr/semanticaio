FROM semanticaio-python-base

WORKDIR /opt/service
ADD config ./config
ADD src/lib ./lib
ADD ./src/classifier/__init__.py ./__init__.py
ADD ./src/classifier/main.py ./main.py
CMD THEANO_FLAGS=mode=FAST_RUN,device=cpu,floatX=float32 python -u main.py
