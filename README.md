# TermiDator
a killer solution

## Style Guide
- Black formatter

## Architecture
- backend
  - REST server that handles data streaming and triggers batch processing jobs
- power_bi
  - data visualization and analysis tool
- db
  - Postgres database (datalake)

![Architecture](./architecture.png)
---
|Technology|Pros|Cons|
|----------|----|----|
|Postgres|on-prem: platform independent|it's an OLTP databse, not OLAP because it's a row DB|
|Python|Easy to program and understand|slow, interpreted, huge Heap allocation|
|Django|Easy DB Model building and migration|It's ORM is not designed for DataStreaming nor DWH building, performance is lacking|
|Jupyter Notebooks|Ease of use, Open Source, easy to integrate|Not the most professional data visualization|

PS: if we trully wanted to scale we'd directly upload to a cloud provider and do stream and batch processing with Spark (orchestrated with Ariflow most probably) on top of a columnar DataBase

## Alternatives we looked at
- https://theorangeone.net/posts/django-orm-performance/
- https://docs.djangoproject.com/en/dev/topics/db/sql/#executing-custom-sql-directly
- https://pypi.org/project/beam-postgres/
- https://www.psycopg.org/docs/

