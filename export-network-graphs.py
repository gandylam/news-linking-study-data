"""
Generate one directed weighted network graph per country. Nodes are media sources, edges are weighted number of links
between them.
"""

import logging
import pandas as pd
import networkx as nx

import analyzer.util.collections as collections
import analyzer.util.domains as domains

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    df = pd.read_csv("export/links-by-media/all-links.csv")
    # grab only the columns we need
    df = df[['source_stories_id', 'source_country', 'source_domain', 'target_domain']]
    # remove self_links
    df = df[df['source_domain'] != df['target_domain']]
    # remove invalid links
    df = df.dropna()

    countries = ['IND', 'GBR', 'KEN', 'ZAF', 'AUS', 'PHL']

    for c in countries:
        logging.info("Working on {}".format(c))
        cdf = df[df['source_country'] == c]
        # transform directed pairs of source/target domains into a new dataset, capturing sum in a "weight" column
        cdf = cdf.groupby(['source_domain', 'target_domain']).size().to_frame('weight').reset_index()
        G = nx.from_pandas_edgelist(cdf, 'source_domain', 'target_domain', 'weight', nx.DiGraph)
        # category captures national collection, platform, search engine, or unknown
        nx.set_node_attributes(G, 'Unknown', 'category')
        nx.set_node_attributes(G, 'Unknown', 'media_type')
        # add in media source metadata
        media = collections.media_for_country(c)
        media_attributes = {}
        for m in media:
            media_attributes[m['domain']] = dict(
                category='National Media Source',
                domain=m['domain'],
                media_type=m['metadata']['media_type']['label'] if m['metadata']['media_type'] else 'Uknown',
                url=m['url'],
                media_id=m['media_id'],
                name=m['name'],
                stories_per_day=m['num_stories_90']/90,
                country=c,
                pub_state=m['metadata']['pub_state']['label'] if m['metadata']['pub_state'] else 'Unknown',
                language=m['metadata']['language']['label'] if m['metadata']['language'] else 'Unknown',
            )
        nx.set_node_attributes(G, media_attributes)
        # and mark social media platforms
        platform_attributes = {}
        for d in domains.PLATFORM_DOMAINS:
            platform_attributes[d] = dict(
                category="Platform",
                domain=d,
                media_type="Platform"
            )
        nx.set_node_attributes(G, platform_attributes)
        # and mark social media platforms
        search_engine_attributes = {}
        for d in domains.SEARCH_ENGINE_DOMAINS:
            search_engine_attributes[d] = dict(
                category="Search Engine",
                domain=d,
                media_type="Search Engine"
            )
        nx.set_node_attributes(G, search_engine_attributes)
        # save the network out for use
        nx.write_gexf(G, 'export/country-networks/{}.gexf'.format(c))
