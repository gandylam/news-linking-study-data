import logging
import os
import io
import json
from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

INPUT_DIR = "input"
OUTPUT_DIR = os.path.join("export", "tmp")

RUN_PARALLEL = True


def media_dir_export_worker(dir: str) -> None:
    logging.info("Working on {}".format(dir))
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    files = [os.path.join(dir, f) for f in os.listdir(dir)
             if os.path.isfile(os.path.join(dir, f)) and f.endswith('.json')]
    if len(files) == 0:
        logging.info("  Skipping - no files")
        return
    logging.info("  Found {} story files".format(len(files)))
    # find data
    all_target_domains = set([])
    for story_file in files:
        with open(story_file) as f2:
            story = json.load(f2)
        story_target_domains = set([link['target_domain'] for link in story['links']])
        all_target_domains = set.union(all_target_domains, story_target_domains)
    # write output
    export_file_name = dir.split("/")[-1] + "-targets.txt"
    logging.info("  Export {} target domains to {}".format(len(all_target_domains), export_file_name))
    with io.open(os.path.join(OUTPUT_DIR, export_file_name), 'w', encoding='utf8') as output_file:
        for item in all_target_domains:
            output_file.write(item + "\n")
    logging.info("  Finished {} stories from {} - {} target domains".format(len(files), dir, len(all_target_domains)))


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

