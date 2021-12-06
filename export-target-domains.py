import logging
import os
import io
import json
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

INPUT_DIR = "export/links-by-media/csv"
OUTPUT_DIR = "export/domain-links-by-media/"

RUN_PARALLEL = True


def media_dir_export_worker(file: str) -> None:
    logging.info("Working on {}".format(file))
    df = pd.read_csv(file)
    target_domains = df['target_domain'].unique()
    # write it out
    output = os.path.join(OUTPUT_DIR, file.split("/")[-1])
    with open(output, "w") as f:
        for d in target_domains:
            f.write(d + "\n")
    logging.info("  Finished {} domains to {}".format(len(target_domains), output))


if __name__ == '__main__':
    logging.info("Reading input files from {}/".format(INPUT_DIR))
    files = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR)
             if os.path.isfile(os.path.join(INPUT_DIR, f)) and f.endswith('.csv')]
    logging.info("Found {} media CSV files to process".format(len(files)))
    if RUN_PARALLEL:
        with ProcessPoolExecutor(max_workers=12) as executor:
            _ = executor.map(media_dir_export_worker, files)
    else:
        for f in files:
            media_dir_export_worker(f)

