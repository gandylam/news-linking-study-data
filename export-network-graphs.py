import logging
import pandas as pd
import networkx as nx

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
        cdf = cdf.groupby(['source_domain', 'target_domain']).size().to_frame('weight').reset_index()
        G = nx.from_pandas_edgelist(cdf, 'source_domain', 'target_domain', 'weight', nx.DiGraph)
        nx.write_gexf(G, 'export/country-networks/{}.gexf'.format(c))
