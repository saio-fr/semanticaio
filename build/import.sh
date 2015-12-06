docker build -t semanticaio-import -f ./build/import/Dockerfile .
docker run --rm \
  --name semanticaio-import \
  --volumes-from semanticaio-data \
  semanticaio-import
docker rmi semanticaio-import
