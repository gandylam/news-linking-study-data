Linking in the News Study Data Processor
========================================

Code to generate data for a study into cross-national linking norms in online news.

## Process

1. Download all the stories with HTML into the `input` folder - there should be one folder per media source in there
2. Run `run-pipeline.sh` to run the analysis on all the stories (this adds metadata to each existing file)
3. Run `run-export-links.sh` to export the metadata added by the pipe to ndjson/csv (in `export/links-by-media`) 
4. Combine the CSV files into one: `csvstack export/links-by-media/csv/*.csv > export/links-by-media/all.csv` for use
with Tableau or R Studio
5. Combine the NDJSON files into one: `cat export/links-by-media/ndjson/*.ndjson > export/links-by-media/all.ndjson`

## Imoporting to Kibana

To export to our Media Cloud Kibana:
 * setup tunnel to Kibana `ssh -6 -L 9200:$(ssh -6 bly.srv.mediacloud.org dokku elasticsearch:info kibana-elasticsearch --internal-ip):9200 bly.srv.mediacloud.org`
 * run import: `elasticsearch_loader --es-host http://[::1]:9200/ --index linkstudy-1 --index-settings-file export/story-link-mapping.json json export/story-links-sample1.ndjson --json-lines`
 