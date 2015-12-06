# todo build web server
docker build -t semanticaio-controller -f ./build/controller/Dockerfile .
docker build -t semanticaio-matcher -f ./build/matcher/Dockerfile .
docker build -t semanticaio-classifier -f ./build/classifier/Dockerfile .
docker build -t semanticaio-classifier-trainer -f ./build/classifier-trainer/Dockerfile .
docker build -t semanticaio-encoder -f ./build/encoder/Dockerfile .
docker build -t semanticaio-encoder-trainer -f ./build/encoder-trainer/Dockerfile .
