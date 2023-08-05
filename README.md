# <u>***TermiDator***</u>
#### *a killer solution*

### Style Guide
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
|Python|Easy to code and understand|slow, interpreted, huge Heap allocation|
|Django|Easy DB Model building and migration|It's ORM is not designed for DataStreaming nor DWH building, performance is lacking|
|Jupyter Notebooks|Ease of use, Open Source, easy to integrate|Not the most professional data visualization|
|PostGIS|Easy plug and play extension for Postgres|Supports up to 4D vectors|


PS: if we trully wanted to scale we'd directly upload to a cloud provider and do stream and batch processing with Spark (orchestrated with Ariflow most probably) on top of a columnar DB

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
- Resources for docker QEMU VM
  - 6 threads
  - 16GB RAM
  - 1,5GB Swap
  - 200GB Disk
- Idle resource utilization (100% CPU means 1 thread)
![](./images/idle_backend.png)

---
During streaming of amazon_metadata
- Time (seconds)
  - /server/backend 
  ![](./images/metadata_etl.png)
  - /server/backend/data/streamer.py
  ![](./images/metadata_etl_client.png)
- Resources
  - /server/backend 
  ![](./images/metadata_docker.png)
  - /server/backend/data/streamer.py
  ![](./images/metadata_processes.png)
  - Overall:
  ![](./images/metadata_cpu.png)

(most of the payload goes straight to the garbage)

---
During streaming of amazon_reviews
- Time (seconds) for 55826 entries 
  - /server/backend 
  ![](./images/review_backend.png)
  - /server/backend/data/streamer.py
  ![](./images/review_client.png)
- Resources
  - /server/backend
  ![](./images/review_backend_resource.png)
  - /server/backend/data/streamer.py
  ![](./images/review_client_resource.png)
  - Overall
  ![](./images/review_overall_resource.png)

---
During streaming of emotion analysis of reviews
- Time: 
  - ~ 10 ms per entry or even less, couldn't measure properly because of asyncio
- Resources
  - /server/backend 
  ![](./images/emotions_streaming_server.png)
  - /server/notebooks/nlp/emotions_classifier.py
  ![](./images/emotions_streaming_client.png)
  - Overall:
  ![](./images/emotions_streaming_overall.png)


---
During updating of PCA embeddings for review emotions
- Time: ~ 12 ms per asin. ~ 3 minutes total for ~ 150k emotionally pre-processed reviews. Didn't even bother to use asyncio

---
Fetching closest (knn) review to the average for that asin
- Time for an asin with 2562 reviews processed
  - /server/backend 
  ![](./images/pca_backend.png)
  - /server/notebooks/utils.py
  ![](./images/pca_client.png)
