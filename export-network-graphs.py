"""
Generate one directed weighted network graph per country. Nodes are media sources, edges are weighted number of links
between them.
"""

import logging
import pandas as pd
import networkx as nx
import sys
import os
import json

import analyzer.util.collections as collections
import analyzer.util.domains as domains

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

COUNTRIES = ['IND', 'GBR', 'KEN', 'ZAF', 'AUS', 'PHL', 'USA']

if __name__ == '__main__':

    # pre-load the list of domain info from Media Cloud
    media2info = {d['domain']:d for d in json.load(open(os.path.join('export', 'all-domains.json')))}

    # load the list of all links, to turn into a graph
    df = pd.read_csv("export/links-by-media/all.csv")
    df = df[['source_stories_id', 'source_country', 'source_domain', 'target_domain']]  # grab only the columns we need
    df = df[df['source_domain'] != df['target_domain']]  # remove self_links
    df = df.dropna()  # remove invalid links

    # now build the graph for each country
    for country_alpha3 in COUNTRIES:
        logging.info("Working on {}".format(country_alpha3))
        cdf = df[df['source_country'] == country_alpha3]
        # transform directed pairs of source/target domains into a new dataset, capturing sum in a "weight" column
        cdf = cdf.groupby(['source_domain', 'target_domain']).size().to_frame('weight').reset_index()
        G = nx.from_pandas_edgelist(cdf, 'source_domain', 'target_domain', 'weight', nx.DiGraph)
        # category captures national collection, platform, search engine, or unknown
        nx.set_node_attributes(G, 'Unknown', 'category')
        nx.set_node_attributes(G, 'Unknown', 'media_type')
        # add in media source metadata
        try:
            country_media2info = {m['domain']: m for m in collections.media_for_country(country_alpha3)}
        except FileNotFoundError:
            logger.error("Can't find list of media sources for {} - metadata will be missing on nodes".format(country_alpha3))
            sys.exit()
        # now add categories to other domains, based on some heuristics
        node_attributes = {}
        for n in G.nodes():
            details = None
            if n in country_media2info:
                # the domain is in this country's national collection (ie. the source of our corpus)
                m = country_media2info[n]
                details = dict(
                    category='National Media Source',
                    domain=m['domain'],
                    media_type=m['metadata']['media_type']['label'] if m['metadata']['media_type'] else 'Unknown',
                    url=m['url'],
                    media_id=m['media_id'],
                    name=m['name'],
                    stories_per_day=m['num_stories_90']/90,
                    country=country_alpha3,
                    pub_state=m['metadata']['pub_state']['label'] if m['metadata']['pub_state'] else 'Unknown',
                    language=m['metadata']['language']['label'] if m['metadata']['language'] else 'Unknown',
                )
            elif n in domains.PLATFORM_DOMAINS:
                # the domain is a platform like YouTube or Facebook
                details = dict(category="Platform", domain=n)
            elif n in domains.SEARCH_ENGINE_DOMAINS:
                # the domain is a search engine like Google
                details = dict(category="Search Engine", domain=n)
            elif domains.is_government_domain(n):
                # the domain is an official source, like un.int, worldbank.org, or stats.gov.ph
                details = dict(category="Government", domain=n)
            elif domains.is_educational_domain(n):
                # the domain is a university (ie. *.edu)
                details = dict(category="Educational", domain=n)
            elif n in media2info:
                # the domain is in Media Cloud
                m = media2info[n]
                details = dict(
                    category='National Media Source' if domains.has_country_suffix(n, country_alpha3) else 'Media Source',
                    domain=m['domain'],
                    media_type=m['metadata']['media_type']['label'] if m['metadata']['media_type'] else 'Unknown',
                    url=m['url'],
                    media_id=m['media_id'],
                    name=m['name'],
                    stories_per_day=m['num_stories_90']/90,
                    country=country_alpha3 if domains.has_country_suffix(n, country_alpha3) else '',
                    pub_state=m['metadata']['pub_state']['label'] if m['metadata']['pub_state'] else 'Unknown',
                    language=m['metadata']['language']['label'] if m['metadata']['language'] else 'Unknown',
                )
            elif domains.has_country_suffix(n, country_alpha3):
                # the domain is published in this country
                details = dict(category='National Media Source', domain=n, country=country_alpha3)
            else:
                details = dict(domain=n)
            if details is not None:
                node_attributes[n] = details
        nx.set_node_attributes(G, node_attributes)
        # save the country's network so we can use it Gephi
        nx.write_gexf(G, 'export/country-networks/{}.gexf'.format(country_alpha3))
