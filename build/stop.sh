# todo stop web server
docker stop semanticaio-controller
docker stop semanticaio-matcher
docker stop semanticaio-classifier
docker stop semanticaio-classifier-trainer
docker stop semanticaio-encoder
docker stop semanticaio-encoder-trainer
# todo rm web server
docker rm semanticaio-controller
docker rm semanticaio-matcher
docker rm semanticaio-classifier
docker rm semanticaio-classifier-trainer
docker rm semanticaio-encoder
docker rm semanticaio-encoder-trainer
