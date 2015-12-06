docker run -d \
  --name semanticaio-encoder \
  --link semanticaio-crossbar:crossbar \
  --volumes-from semanticaio-data \
  semanticaio-encoder

docker run -d \
  --name semanticaio-encoder-trainer \
  --link semanticaio-crossbar:crossbar \
  --volumes-from semanticaio-data \
  semanticaio-encoder-trainer

docker run -d \
  --name semanticaio-classifier \
  --link semanticaio-crossbar:crossbar \
  --volumes-from semanticaio-data \
  semanticaio-classifier

docker run -d \
  --name semanticaio-classifier-trainer \
  --link semanticaio-crossbar:crossbar \
  --volumes-from semanticaio-data \
  semanticaio-classifier-trainer

docker run -d \
  --name semanticaio-matcher \
  --link semanticaio-crossbar:crossbar \
  --volumes-from semanticaio-data \
  semanticaio-matcher

docker run -d \
  --name semanticaio-controller \
  --link semanticaio-crossbar:crossbar \
  semanticaio-controller

# TODO start web-server
