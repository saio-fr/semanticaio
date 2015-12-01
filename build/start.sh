docker run -d \
  --name semanticaio-classifier \
  --link semanticaio-crossbar:crossbar \
  -v $(pwd)/data/classifier:/opt/service/data \
  semanticaio-classifier

docker run -d \
  --name semanticaio-classifier-trainer \
  -v $(pwd)/data/classifier:/opt/service/data \
  --link semanticaio-crossbar:crossbar \
  semanticaio-classifier-trainer

docker run -d \
  --name semanticaio-controller \
  --link semanticaio-crossbar:crossbar \
  semanticaio-controller

docker run -d \
  --name semanticaio-database \
  --link semanticaio-crossbar:crossbar \
  --link semanticaio-postgres:postgres \
  semanticaio-database

docker run -d \
  --name semanticaio-encoder \
  --link semanticaio-crossbar:crossbar \
  -v $(pwd)/data/encoder:/opt/service/data \
  semanticaio-encoder

docker run -d \
  --name semanticaio-encoder-trainer \
  -v $(pwd)/data/encoder:/opt/service/data \
  --link semanticaio-crossbar:crossbar \
  semanticaio-encoder-trainer

docker run -d \
  --name semanticaio-matcher \
  --link semanticaio-crossbar:crossbar \
  semanticaio-matcher

docker run -d \
  --name semanticaio-tagger \
  --link semanticaio-crossbar:crossbar \
  -v $(pwd)/data/tagger:/opt/service/data \
  semanticaio-tagger

docker run -d \
  --name semanticaio-tagger-trainer \
  -v $(pwd)/data/tagger:/opt/service/data \
  --link semanticaio-crossbar:crossbar \
  semanticaio-tagger-trainer

# TODO start web-server
