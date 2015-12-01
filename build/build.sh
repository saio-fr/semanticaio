docker build -t semanticaio-classifier -f ./build/classifier/Dockerfile .
docker build -t semanticaio-classifier-trainer -f ./build/classifier-trainer/Dockerfile .
docker build -t semanticaio-controller -f ./build/controller/Dockerfile .
docker build -t semanticaio-database -f ./build/database/Dockerfile .
docker build -t semanticaio-encoder -f ./build/encoder/Dockerfile .
docker build -t semanticaio-encoder-trainer -f ./build/encoder-trainer/Dockerfile .
docker build -t semanticaio-matcher -f ./build/matcher/Dockerfile .
docker build -t semanticaio-tagger -f ./build/tagger/Dockerfile .
docker build -t semanticaio-tagger-trainer -f ./build/tagger-trainer/Dockerfile .
# todo build web server
