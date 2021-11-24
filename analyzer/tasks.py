import json
import io
import csv
from typing import Dict, List
import os
import prefect
from prefect import task

import analyzer.analysis as analysis
from analyzer.util.domains import get_canonical_mediacloud_domain


@task
def list_json_files_in_dir(input_dir: str) -> List:
    logger = prefect.context.get("logger")
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)
             if os.path.isfile(os.path.join(input_dir, f)) and f.endswith('.json')]
    logger.info("    found {} files".format(len(files)))
    return files


@task
def get_link_data_from_story(file_path: str) -> List[Dict]:
    story = json.load(open(file_path))
    # parse out the links we care about
    content = analysis.extract_content(story['raw_first_download_file'])
    content_only_link_tags = analysis.remove_non_link_tags(content)
    sentences = analysis.sentence_tokenization(content_only_link_tags)
    links = analysis.all_links(sentences)
    # and prep a bunch of metadata
    country = analysis.country_alpha3(story['media_id'])
    week_index = analysis.study_week_index(story['publish_date'])
    theme_data = analysis.nyt_theme(story['story_tags'])
    source_domain = get_canonical_mediacloud_domain(story['url'])
    # setup the links with all metadata
    data = [dict(
        link_id="{}-{}".format(story['stories_id'], link['link_id']),  # so we a unique id for this link
        link_text=link['link_text'],
        sentence=link['sentence'].replace("\n", " ").replace("\t", " "),  # remove EOL and tab so it is more readable
        target_url=link['target_url'],
        source_stories_id=story['stories_id'],
        publication_date=story['publish_date'][0:19],  # strip off milliseconds
        source_url=story['url'],
        source_domain=source_domain,
        target_domain=link['target_domain'],
        source_country=country,
        week_number=week_index,
        source_nyt_themes=theme_data['nyt_theme_tag_ids'],
        source_story_is_politics=theme_data['is_politics'],
        source_story_is_health=theme_data['is_health'],
        source_story_is_economics=theme_data['is_economics'],
        source_story_is_sports=theme_data['is_sports'],
        source_story_sentence_count=len(sentences),
        is_self_link=(source_domain == link['target_domain']),
    ) for link in links]
    return data


@task
def write_json_link_file(csv_file_path: str, ndjson_file_path: str, links_per_story: List[List[Dict]]) -> None:
    logger = prefect.context.get("logger")
    field_names = ["link_id", "source_stories_id", "publication_date", "sentence", "source_url", "source_domain", "link_text", "target_url", "target_domain", "source_country", "week_number", "source_nyt_themes", "source_story_is_politics", "source_story_is_health", "source_story_is_economics", "source_story_sentence_count", "source_story_is_sports", "is_self_link"]
    csv_writer = csv.DictWriter(io.open(csv_file_path, 'w', encoding='utf8'), field_names, extrasaction='ignore')
    csv_writer.writeheader()
    ndjson_file = io.open(ndjson_file_path, 'w', encoding='utf8')
    # flatten list of list of dicts
    links = []
    for story_links in links_per_story:
        links += story_links
    logger.info("    need to write {} links".format(len(links)))
    # and export the links
    for link in links:
        ndjson_file.write(json.dumps(link, ensure_ascii=False)+"\n")
        csv_writer.writerow(link)
