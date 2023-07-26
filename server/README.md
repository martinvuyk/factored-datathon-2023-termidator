### Deploy:

1. download folder
2. make a .env file with the following fields:
  - SQL_ENGINE=django.db.backends.postgresql
  - SQL_DATABASE=
  - SQL_USER=
  - SQL_PASSWORD=
  - SQL_HOST=db
  - SQL_PORT=5432
  - BACKEND_HOST=IPv4_addr
  - BACKEND_PORT=4595
  - SAS_URL=
  - SAS_TOKEN=
3. write in a terminal: "docker compose up"

#### Requirements:
- Docker
