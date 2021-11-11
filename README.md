Linking in the News Study Data Processor
========================================

Code to generate data for a study into cross-national linking norms in online news.

## Architecture

This works off a simple architecture for a (slightly) generic pipeline for processing Media Cloud story data in a 
MongoDB database. You create up a series of `Stage`s - small, easily testable functions that take a story `Dict` as 
input, and then output a `Dict` of new information to add to it. `Stage`s are linked together in an ordered `Pipeline`.
Stories are moved through the `Pipeline` via a RabbitMQ-baked Celery queue. You execute `run-pipeline.py` to fill the
queue with one job for each story that is ready to move to the next stage. Once those jobs are all processed you can 
check your database and run it again. Keep going as needed until they've all reached the final stage. The stage data is 
stored on the stories themselves in a `_pipeline` property that is added. 

## Process

### Files

1. Download all the stories with HTML into the `input` folder - there should be one folder per media source in there
2. Run `run-pipeline.sh` to run the analysis on all the stories (this adds metadata to each existing file)
3. Run `run-export-links.sh` to export the metadata added by the pipe to ndjson/csv (in `export/links-by-media`) 
4. Combine the CSV files into one: `csvstack export/links-by-media/csv/*.csv > export/links-by-media/all.csv`

### Database (previous/slower)

1. Download all the stories into a Mongo Database
2. Set those connection parameters in a `.env` file.
3. Run celery to handle jobs: `celery -A analyzer worker -l info --concurrency=16`
4. Then run `run-pipeline.py` over and over until all the data is moved through the pipeline.
5. Then run `export-links.py` to create an ndjson/csv for import into Kibana or Tableau. 

## Imoporting to Kibana

To export to our Media Cloud Kibana:
 * setup tunnel to Kibana `ssh -6 -L 9200:$(ssh -6 bly.srv.mediacloud.org dokku elasticsearch:info kibana-elasticsearch --internal-ip):9200 bly.srv.mediacloud.org`
 * run import: `elasticsearch_loader --es-host http://[::1]:9200/ --index linkstudy-1 --index-settings-file export/story-link-mapping.json json export/story-links-sample1.ndjson --json-lines`
 