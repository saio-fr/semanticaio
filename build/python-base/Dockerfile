FROM ermaker/keras

RUN pip install scikit-learn
RUN pip install autobahn

RUN mkdir -p /opt/service
WORKDIR /opt/service
ADD config ./config
ADD src/lib ./lib
CMD THEANO_FLAGS=mode=FAST_RUN,device=cpu,floatX=float32 python main.py
