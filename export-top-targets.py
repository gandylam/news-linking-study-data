import pandas as pd
import os.path
import logging

from analyzer import COUNTRIES
import analyzer.util.domains as domains

logger = logging.getLogger(__file__)

TOP_PCT = 0.05

df = pd.read_csv(os.path.join('export', 'links-by-media', "links-all-no-dupes.csv"))
df = df.dropna()
df = df[df['source_country'].isin(COUNTRIES)]

for c in COUNTRIES:
    country_df = df[df['source_country'] == c]

    # grab top N percent of linked to domains
    agg_country_df = country_df.groupby(['target_domain']).size().reset_index(name='counts')
    sorted_agg_country_df = agg_country_df.sort_values('counts', ascending=False)
    top_agg_country_df = sorted_agg_country_df.head(int(len(sorted_agg_country_df)*TOP_PCT))

    # find category for each
    country_data = []
    for idx, row in top_agg_country_df.iterrows():
        category = domains.get_manual_category(c, row['target_domain'])
        if category is None:
            logger.error("{}: Domain {} has no category".format(c, row['target_domain']))
        country_data.append(dict(
            domain=row['target_domain'],
            category=category if category is not None else '',
            inlinks=row['counts'],
        ))
    country_df = pd.DataFrame(country_data)
    country_df.to_csv('domain-categories-v2-{}.csv'.format(c))
