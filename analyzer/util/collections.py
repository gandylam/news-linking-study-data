import os
import json
import glob
from typing import List, Dict

import analyzer.util.domains as domains

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data_dir = os.path.join(base_dir, "analyzer", "data")

# map from national collection id to country alpha3
with open(os.path.join(data_dir, "country-collections.json")) as f:
    collection_list = json.load(f)
national_collection_2_name_map = {d['country']['national_tags_id']: d['country']['alpha3'] for d in collection_list}
national_name_2_collection_map = {d['country']['alpha3']: d['country']['national_tags_id'] for d in collection_list}

# load up a map from media to the collections is in
media_2_collections = {}
files = glob.glob('{}/analyzer/data/media-in-*.json'.format(base_dir))
for f in files:
    with open(f) as media_list_file:
        media_list = json.load(media_list_file)
        for m in media_list:
            media_collection_ids = [t['tags_id'] for t in m['media_source_tags']]
            media_2_collections[m['media_id']] = media_collection_ids


# map from country alpha3 to list of media
def country_for_media(media_id:int ) -> str:
    global national_collection_2_name_map, media_2_collections
    collections = media_2_collections[media_id]
    for tags_id in collections:
        if tags_id in national_collection_2_name_map:
            return national_collection_2_name_map[tags_id]
    return "???"


def country_national_collection_id(alpha3: str) -> int:
    return national_name_2_collection_map[alpha3]


def media_for_country(alpha3:str) -> List[Dict]:
    # list of media in national collection for country, add in a 'domain' property
    collection_id = national_name_2_collection_map[alpha3]
    with open(os.path.join(data_dir, "media-in-{}.json".format(collection_id))) as f:
        data = json.load(f)
        for media in data:
            media['domain'] = domains.get_canonical_mediacloud_domain(media['url'])
        return data
