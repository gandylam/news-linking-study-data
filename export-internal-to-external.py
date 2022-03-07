import pandas as pd

from analyzer import COUNTRIES
from analyzer.util.domains import PLATFORM_DOMAINS

# load up the dataset
df = pd.read_csv("export/links-by-media/links-all-no-dupes.csv")
df = df.dropna()
df = df[df['source_country'].isin(COUNTRIES)]

# count total links by country
combined_sum_df = df.groupby(['source_country']).size().reset_index(name='total')

# count internal links by country
internal_df = df[df['is_self_link'] == True]
internal_sum_df = internal_df.groupby(['source_country']).size().reset_index(name='internal')

# count external links by country
external_df = df[df['is_self_link'] == False]
external_sum_df = external_df.groupby(['source_country']).size().reset_index(name='external')

# count external links to platforms by country
external_platforms_df = external_df[df['target_domain'].isin(PLATFORM_DOMAINS)]
exeternal_platforms_sum_df = external_platforms_df.groupby(['source_country']).size().reset_index(name='external_platforms')

results_df = combined_sum_df.merge(internal_sum_df).merge(external_sum_df).merge(exeternal_platforms_sum_df)
results_df = results_df.assign(external_not_platforms=results_df['external'] - results_df['external_platforms'],
                               internal_to_external=results_df['internal']/results_df['external'])
results_df = results_df.assign(internal_to_external_no_platforms=results_df['internal']/results_df['external_not_platforms'])
results_df.to_csv('export/internal-to-external.csv', index=False)
