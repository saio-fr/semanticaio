FROM node

RUN echo "//registry.npmjs.org/:_authToken=16b46f03-f1fb-4dce-9a98-c7e685751e67" > ~/.npmrc

RUN mkdir -p /opt/service
WORKDIR /opt/service
ADD config ./config
ADD build/node-base/package.json ./package.json
RUN npm install
