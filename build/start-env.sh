docker run -d \
  --name semanticaio-crossbar \
  -p 50001:8080 \
  semanticaio-crossbar

docker run -d \
  --name semanticaio-postgres \
  -e POSTGRES_PASSWORD=password \
  -v $(pwd)/data/db:/var/lib/postgresql/data \
  postgres

docker run -d \
  --name semanticaio-phppgadmin \
  --link semanticaio-postgres:postgresql \
  -p 50002:80 \
  semanticaio-phppgadmin
