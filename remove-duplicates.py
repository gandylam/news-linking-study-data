import pandas as pd
import os.path

COUNTRIES = ['USA', 'IND', 'GBR', 'KEN', 'ZAF', 'AUS', 'PHL']

# Remove duplicate URLs within each media source

ALL_DATA_FILE = os.path.join('export', 'links-by-media', 'all.csv')
df = pd.read_csv(ALL_DATA_FILE)

# some safety cleaning
df = df.dropna()
df = df[df['source_country'].isin(COUNTRIES)]
print("{} rows total".format(len(df)))

duplicate_link_ids = []
url2id = {}
for index, row in df.iterrows():
    if row['source_url'] not in url2id:
        url2id[row['source_url']] = row['source_stories_id']
    else:
        original_id = url2id[row['source_url']]
        current_id = row['source_stories_id']
        if original_id != current_id:
            duplicate_link_ids.append(row['link_id'])

print("{} duplicate rows".format(len(duplicate_link_ids)))

clean_df = df[~df.link_id.isin(duplicate_link_ids)]
clean_df.to_csv(os.path.join('export', 'links-by-media', 'all-no-dupes.csv'))

print("{} non-duplicate rows".format(len(clean_df)))
