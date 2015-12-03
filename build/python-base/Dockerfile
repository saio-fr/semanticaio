FROM ubuntu

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN curl -qsSLkO \
    https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-`uname -p`.sh \
  && bash Miniconda3-latest-Linux-`uname -p`.sh -b \
  && rm Miniconda3-latest-Linux-`uname -p`.sh
ENV PATH=/root/miniconda3/bin:$PATH
RUN conda install -y theano h5py
RUN pip install keras
RUN pip install scikit-learn
RUN pip install autobahn[asyncio]

RUN mkdir -p /opt/service/data
WORKDIR /opt/service
ADD config ./config
ADD src/lib ./lib
ADD build/python-base/__init__.py ./__init__.py
ADD build/python-base/__init__.py ./lib/__init__.py
