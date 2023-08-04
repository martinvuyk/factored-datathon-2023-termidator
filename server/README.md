# Code:
- backend
  - ./backend/app/views.py
    - endpoint code
  - ./backend/app/models.py
    - db models
- data
  - ./backend/data/streamer.py
    - script for streaming batch data into server
  - ./backend/data/reciever.py
    - script for recieving and storing Azure Eventhub data
- nlp
  - ./notebooks/nlp/emotions_classifier.py
    - Emotion classifier BERT

### Endpoints:
- API
  - base_url/api/v1/
- Documentation
  - base_url/api/v1/docs/swagger

### Deploy:

1. Download folder
2. Make a .env file with the following fields:
  - SQL_ENGINE=django.db.backends.postgresql
  - SQL_DATABASE=
  - SQL_USER=
  - SQL_PASSWORD=
  - SQL_HOST=db
  - SQL_PORT=5432
  - BACKEND_HOST=IPv4_addr
  - BACKEND_PORT=4595
  - LOGLEVEL="DEBUG" | "INFO" | "WARNING"
  - SAS_URL=
  - SAS_TOKEN=
3. Write in a terminal: "docker compose up"

#### Requirements:
- Docker
