FROM semanticaio-python-base

WORKDIR /opt/service
ADD config ./config
ADD src/lib ./lib
ADD ./src/matcher/main.py ./main.py
ADD ./src/matcher/__init__.py ./__init__.py
CMD THEANO_FLAGS=mode=FAST_RUN,device=cpu,floatX=float32 python -u main.py
