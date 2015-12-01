docker build -t semanticaio-test -f ./build/test/Dockerfile .
docker run -d \
  --name semanticaio-test \
  --link semanticaio-crossbar:crossbar \
  semanticaio-test
