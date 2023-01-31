docker build -t autify .

docker run  -dt autify:latest

docker ps

note the container name from the last command

docker exec -it CONTAINER_NAME_HERE bash

python3 main.py https://www.google.com https://www.autify.com

