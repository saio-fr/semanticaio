docker run -d \
  --name semanticaio-crossbar \
  -p 50001:8080 \
  semanticaio-crossbar

docker create \
  --name semanticaio-data \
  -v $(pwd)/data:/opt/service/data \
  semanticaio-python-base
