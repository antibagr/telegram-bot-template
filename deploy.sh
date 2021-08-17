export container_name=chatbot

docker rm -f $container_name &> /dev/null && \
  docker-compose up --remove-orphans --force-recreate --build -d $*

docker logs -f $container_name
