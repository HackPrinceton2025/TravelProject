FROM node:20-alpine

WORKDIR /app

COPY package.json /app/package.json
RUN npm install --silent

COPY . /app

EXPOSE 3000

CMD ["npm", "run", "dev"]


