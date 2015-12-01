docker stop semanticaio-classifier
docker stop semanticaio-classifier-trainer
docker stop semanticaio-controller
docker stop semanticaio-database
docker stop semanticaio-encoder
docker stop semanticaio-encoder-trainer
docker stop semanticaio-matcher
docker stop semanticaio-tagger
docker stop semanticaio-tagger-trainer
# todo stop web server
docker rm -v semanticaio-classifier
docker rm -v semanticaio-classifier-trainer
docker rm semanticaio-controller
docker rm semanticaio-database
docker rm -v semanticaio-encoder
docker rm -v semanticaio-encoder-trainer
docker rm semanticaio-matcher
docker rm -v semanticaio-tagger
docker rm -v semanticaio-tagger-trainer
# todo rm web server
