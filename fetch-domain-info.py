import logging
from typing import Dict, List
from dotenv import load_dotenv
import json
import mediacloud.api
import validators
import os
from prefect import Flow, Parameter
from prefect.executors import LocalDaskExecutor
from prefect import task

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

INPUT_FILE = "export/all-domains.txt"
OUTPUT_FILE = "export/all-domains.json"

RUN_PARALLEL = True


@task
def load_domains_task(input_file_path: str) -> List:
    # load up the domains we need to check out
    logging.info("Reading input from {}".format(input_file_path))
    f = open(input_file_path)
    invalid = 0
    jobs = []
    for line in f.readlines():
        if (len(line) > 0) and validators.domain(line):
            jobs.append(line.strip())
        else:
            invalid += 1
    logging.info("Found {} domains to process ({} invalid)".format(len(jobs), invalid))
    return jobs


@task
def list_media_task(domain: str) -> Dict:
    mc = mediacloud.api.MediaCloud(os.environ.get('MC_API_KEY', None))
    matching_sources = mc.mediaList(name_like=domain)
    if len(matching_sources) == 0:
        return None
    matching_sources[0]['domain'] = domain
    return matching_sources[0]


@task
def write_results_task(output_file: str, media_list: List[Dict]) -> None:
    with open(output_file, 'w') as f:
        json.dump(media_list, f)


if __name__ == '__main__':

    logging.info("Writing results to {}".format(OUTPUT_FILE))

    # now set up the pipeline to run
    with Flow("domain-classification") as flow:
        flow.executor = LocalDaskExecutor(scheduler="threads", num_workers=24)  # execute `map` calls in parallel
        # 1. list all the domains
        input_file = Parameter("input_file", default="domains.txt")
        domains = load_domains_task(input_file)
        # 2. process all the domains (in parallel)
        matching_media = list_media_task.map(domains)
        # 3. save results to json
        json_output_file = Parameter("json_output_file", default="data.json")
        write_results_task(json_output_file, matching_media)

    # run our pipeline
    flow.run(parameters={
        'input_file': INPUT_FILE,
        'json_output_file': OUTPUT_FILE
    })
