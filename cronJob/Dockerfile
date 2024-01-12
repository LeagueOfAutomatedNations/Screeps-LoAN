# syntax=docker/dockerfile:1

FROM node:16.7.0
ENV NODE_ENV=production

WORKDIR /usr/app
COPY . .

RUN npm install --production

CMD [ "node", "index.js" ]