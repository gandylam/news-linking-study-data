Linking in the News Study Data Processor
========================================

Code to generate data for a study into cross-national linking norms in online news.

## Process

1. Download all the stories with HTML into the `input` folder - there should be one folder per media source in there (see below for full query)
2. Run `run-pipeline.sh` to run the analysis on all the stories (this adds metadata to each existing file)
3. Run `run-export-links.sh` to export the metadata added by the pipe to ndjson/csv (in `export/links-by-media`) 
4. Combine the CSV files into one: `csvstack export/links-by-media/csv/*.csv > export/links-by-media/all.csv` for use
with Tableau or R Studio
5. Combine the NDJSON files into one: `cat export/links-by-media/ndjson/*.ndjson > export/links-by-media/all.ndjson`
6. Combine those into one file of all unique domains: `cat export/domain-links-by-media/*.csv | sort | uniq > export/all-domains.txt`
7. Run `python export-domains.py` to write a file for each media source with all the domains link to/from
8. Run `python fetch-domain-info.py` to check for Media Cloud metadata for each media source 
9. Run `python export-network-graphs.py` to generate network graphs for each country, with full source metadata embedded

## Importing to Kibana (optional)

To export to our Media Cloud Kibana:
 * setup tunnel to Kibana `ssh -6 -L 9200:$(ssh -6 bly.srv.mediacloud.org dokku elasticsearch:info kibana-elasticsearch --internal-ip):9200 bly.srv.mediacloud.org`
 * run import: `elasticsearch_loader --es-host http://[::1]:9200/ --index linkstudy-1 --index-settings-file export/story-link-mapping.json json export/story-links-sample1.ndjson --json-lines`
 
## Queries

The original query that created our corpus of stories (matches around 800k stories):

```python
FETCH_TEXT = False
FETCH_RAW_HTML = True
COLLECTIONS = [
    34412476,  # uk national
    34412282,  # Australia national
    34412126,  # Kenya national
    34412238,  # S Africa national
    34412313,  # Philippines national
    34412118,  # India national
    34412234,  # US national
]
QUERY = '* language:en'
FQ = " OR ".join([
    mediacloud.api.MediaCloud.dates_as_query_clause(dt.date(2020, 2, 2), dt.date(2020, 2, 8)),  # inclusive
    mediacloud.api.MediaCloud.dates_as_query_clause(dt.date(2020, 5, 10), dt.date(2020, 5, 16)),  # inclusive
    mediacloud.api.MediaCloud.dates_as_query_clause(dt.date(2020, 8, 16), dt.date(2020, 8, 22)),  # inclusive
    mediacloud.api.MediaCloud.dates_as_query_clause(dt.date(2020, 10, 25), dt.date(2020, 10, 31))  # inclusive
])
LIMIT = None
```
