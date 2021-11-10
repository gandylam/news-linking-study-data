import logging
import os
import io
import csv
import json
from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

INPUT_DIR = "input"
OUTPUT_DIR = os.path.join("export", "links-by-media")
RUN_PARALLEL = True


def media_dir_export_worker(dir: str) -> None:
    logging.info("Working on {}".format(dir))
    ndjson_file_path = os.path.join(OUTPUT_DIR, "ndjson", dir.split("/")[-1] + ".ndjson")
    csv_file_path = os.path.join(OUTPUT_DIR, "csv", dir.split("/")[-1] + ".csv")
    logging.info("  Export to export/links-by-media")
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    files = [os.path.join(dir, f) for f in os.listdir(dir)
             if os.path.isfile(os.path.join(dir, f)) and f.endswith('.json')]
    if len(files) == 0:
        logging.info("  Skipping - no files")
        return
    logging.info("  Found {} story files".format(len(files)))
    ndjson_file = io.open(ndjson_file_path, 'w', encoding='utf8')
    field_names = ["link_id", "source_stories_id", "publication_date", "sentence", "source_url", "source_domain", "link_text", "target_url", "target_domain", "source_country", "week_number", "source_nyt_themes", "source_story_is_politics", "source_story_is_health", "source_story_is_economics", "source_story_sentence_count", "source_story_is_sports", "is_self_link"]
    csv_writer = csv.DictWriter(io.open(csv_file_path, 'w', encoding='utf8'), field_names, extrasaction='ignore')
    csv_writer.writeheader()
    for story_file in files:
        with open(story_file) as f2:
            story = json.load(f2)
        for link in story['links']:
            link['publication_date'] = link['publication_date'][0:19]  # strip off milliseconds
            ndjson_file.write(json.dumps(link, ensure_ascii=False)+"\n")
            csv_writer.writerow(link)
    logging.info("  Finished {} stories from {}".format(len(files), dir))


if __name__ == '__main__':
    logging.info("Reading input files from {}/".format(INPUT_DIR))
    media_dirs = [os.path.join(INPUT_DIR, f) for f in os.listdir("input") if os.path.isdir(os.path.join(INPUT_DIR, f))]
    logging.info("Found {} media dirs to process".format(len(media_dirs)))
    if RUN_PARALLEL:
        with ProcessPoolExecutor(max_workers=12) as executor:
            _ = executor.map(media_dir_export_worker, media_dirs)
    else:
        for media_dir in media_dirs:
            media_dir_export_worker(media_dir)

