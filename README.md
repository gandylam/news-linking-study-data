Story Analyzer
==============

## Process

First download all the stories into a Mongo database. Then set those connection parameters in a .env file.

Run celery to handle jobs: `celery -A analyzer worker -l debug --concurrency=16`

Then run `run-pipeline.py` over and over until all the data is moved through the pipeline.

Then run `export-data.py` to create an ndjson for import into Kibana.

Import into Kibana:
