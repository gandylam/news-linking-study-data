import logging
import os
from concurrent.futures import ProcessPoolExecutor

from urlstudy.pipeline import my_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)
# silence the "ruthless removal did not work" INFO logs
readability_logger = logging.getLogger('readability.readability')
readability_logger.propagate = False

INPUT_DIR = "input"
RUN_PARALLEL = True


def media_dir_worker(dir: str) -> None:
    logging.info("Working on {}".format(dir))
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    files = [os.path.join(dir, f) for f in os.listdir(dir)
             if os.path.isfile(os.path.join(dir, f)) and f.endswith('.json')]
    if len(files) == 0:
        logging.info("  Skipping - no files")
        return
    logging.info("  Found {} story files".format(len(files)))
    for story_file in files:
        my_pipeline.process_file(story_file)
        logging.debug("  done with {}".format(story_file))
    logging.info("  Finished {} stories from {}".format(len(files), dir))


if __name__ == '__main__':
    logging.info("Reading input files from {}/".format(INPUT_DIR))
    media_dirs = [os.path.join(INPUT_DIR, f) for f in os.listdir("input") if os.path.isdir(os.path.join(INPUT_DIR, f))]
    logging.info("Found {} media dirs to process".format(len(media_dirs)))
    if RUN_PARALLEL:
        with ProcessPoolExecutor(max_workers=12) as executor:
            _ = executor.map(media_dir_worker, media_dirs)
    else:
        for media_dir in media_dirs:
            media_dir_worker(media_dir)
