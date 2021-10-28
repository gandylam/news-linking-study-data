import logging
import os
import io
import json
from concurrent.futures import ProcessPoolExecutor

from urlstudy.pipeline import my_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

INPUT_DIR = "input"
OUTPUT_DIR = os.path.join("export", "by_media")
RUN_PARALLEL = False


def media_dir_export_worker(dir: str) -> None:
    logging.info("Working on {}".format(dir))
    export_file_name = dir.split("/")[-1] + ".ndjson"
    logging.info("  Export to {}".format(export_file_name))
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    files = [os.path.join(dir, f) for f in os.listdir(dir)
             if os.path.isfile(os.path.join(dir, f)) and f.endswith('.json')]
    if len(files) == 0:
        logging.info("  Skipping - no files")
        return
    logging.info("  Found {} story files".format(len(files)))
    with io.open(os.path.join(OUTPUT_DIR, export_file_name), 'w', encoding='utf8') as output_file:
        for story_file in files:
            with open(story_file) as f2:
                story = json.load(f2)
            for link in story['links']:
                link['publication_date'] = link['publication_date'][0:19]  # strip off milliseconds
                output_file.write(json.dumps(link, ensure_ascii=False)+"\n")
    logging.info("  Finished {} stories from {}".format(len(files), dir))


if __name__ == '__main__':
    logging.info("Reading input files from {}/".format(INPUT_DIR))
    media_dirs = [os.path.join(INPUT_DIR, f) for f in os.listdir("input") if os.path.isdir(os.path.join(INPUT_DIR, f))]
    logging.info("Found {} media dirs to process".format(len(media_dirs)))
    if RUN_PARALLEL:
        with ProcessPoolExecutor(max_workers=12) as executor:
            _ = executor.map(media_dir_export_worker, media_dirs)
    else:
        for media_dir in media_dirs[:3]:
            media_dir_export_worker(media_dir)

