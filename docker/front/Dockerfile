FROM node:17-alpine AS node

# For webpack:
# https://github.com/webpack/webpack/issues/14532
ENV NODE_OPTIONS=--openssl-legacy-provider
ADD ./front /app

WORKDIR /app
RUN npm i

ENTRYPOINT [ "npm", "run", "dev" ]

FROM node AS build

RUN npm run build

FROM nginx:1.21-alpine AS final

COPY --from=build /app/dist/static /usr/share/nginx/html
COPY --from=build /app/dist/index.html /usr/share/nginx/html
