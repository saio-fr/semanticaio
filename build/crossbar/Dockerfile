FROM vinelab/crossbar

RUN mkdir -p /opt/service/.crossbar
WORKDIR /opt/service

ADD ./config/crossbar.json ./.crossbar/config.json

ENTRYPOINT ["crossbar","start"]
