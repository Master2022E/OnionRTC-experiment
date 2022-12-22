FROM ubuntu

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
     && apt-get -y install --no-install-recommends make python3 python3-pip

WORKDIR /app
COPY . .
RUN python3 -m pip install -r requirements.txt

CMD [ "python3", "controller.py" ]