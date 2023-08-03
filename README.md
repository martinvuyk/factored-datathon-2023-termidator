# TermiDator
a killer solution

## Style Guide
- Black formatter

## Architecture
- backend
  - REST server that handles data streaming and triggers batch processing jobs
- Jupyter Notebooks
  - data visualization and analysis tool
- db
  - Postgres database (datalake)

![Architecture](./images/architecture.png)
---
|Technology|Pros|Cons|
|----------|----|----|
|Postgres|on-prem: platform independent|it's an OLTP databse, not OLAP because it's a row DB|
|Python|Easy to program and understand|slow, interpreted, huge Heap allocation|
|Django|Easy DB Model building and migration|It's ORM is not designed for DataStreaming nor DWH building, performance is lacking|
|Jupyter Notebooks|Ease of use, Open Source, easy to integrate|Not the most professional data visualization|
|PostGIS|Easy plug and play extension for Postgres|Supports up to 4D vectors|


PS: if we trully wanted to scale we'd directly upload to a cloud provider and do stream and batch processing with Spark (orchestrated with Ariflow most probably) on top of a columnar DataBase

![DB_SCHEMA](./images/db_schema.png)

## Alternatives we looked at
- https://github.com/pgvector/pgvector
- https://theorangeone.net/posts/django-orm-performance/
- https://docs.djangoproject.com/en/dev/topics/db/sql/#executing-custom-sql-directly
- https://pypi.org/project/beam-postgres/
- https://www.psycopg.org/docs/


# Performance:
- Machine specs: 
  - Intel® Core™ i7-7700HQ CPU @2.80GHz,  8 threads
  - 32GB RAM @2667 MT/s, 1.2V
- Resources for docker QUEMU VM
  - 6 threads
  - 16GB RAM
  - 1,5GB Swap
  - 96GB Disk
- Idle resource utilization
![](./images/idle_backend.png)

---
During streaming of amazon_metadata
- /server/backend 
![](./images/metadata_etl.png)
![](./images/metadata_docker.png)
- /server/backend/data/streamer.py
![](./images/metadata_etl_client.png)
![](./images/metadata_processes.png)
- Overall:
![](./images/metadata_cpu.png)

---
During streaming of amazon_reviews
- /server/backend 
![](./images/review_backend.png)
- /server/backend/data/streamer.py
![](./images/review_client.png)

for 55826 entries

---
During streaming of emotion analysis of reviews
- /server/backend 
![](./images/streaming_review_emotions.png)
- /server/notebooks/nlp/emotions_classifier.py
![](./images/nlp_streaming_review_emotions.png)

Time: ~ 110-140 ms per entry

---