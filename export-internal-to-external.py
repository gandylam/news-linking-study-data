import pandas as pd

PLATFORM_DOMAINS = ["acast.com", "facebook.com", "fb.com", "fb.org", "flickr.com", "imgur.com", "instagram.com", "linkedin.com", "linktr.ee", "medium.com", "omny.fm", "patreon.com", "pinterest.com", "qq.com", "reddit.com", "scribd.com", "soundcloud.com", "spotify.com", "tiktok.com", "twitch.tv", "twitter.com", "vimeo.com", "weibo.com", "whatsapp.com", "yahoo.com", "youtu.be", "youtube.com" ]
COUNTRIES = ['USA', 'IND', 'GBR', 'KEN', 'ZAF', 'AUS', 'PHL']

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

# count external links (without platforms) by country
external_platforms_df = external_df[df['target_domain'].isin(PLATFORM_DOMAINS)]
exeternal_platforms_sum_df = external_platforms_df.groupby(['source_country']).size().reset_index(name='external_platforms')

results_df = combined_sum_df.merge(internal_sum_df).merge(external_sum_df).merge(exeternal_platforms_sum_df)
results_df = results_df.assign(external_not_platforms=results_df['external'] - results_df['external_platforms'],
                               internal_to_external=results_df['internal']/results_df['external'])
results_df = results_df.assign(internal_to_external_no_platforms=results_df['internal']/results_df['external_not_platforms'])
results_df.to_csv('export/internal-to-external.csv', index=False)
