FROM node:20

WORKDIR /app

# Instala cliente Postgres (para pg_isready se precisar de healthcheck)
RUN apt-get update && apt-get install -y postgresql-client

# Copia package.json e instala dependências
COPY package.json package-lock.json* ./
RUN npm install

# Copia schema Prisma, migrations e seed
COPY prisma ./prisma

