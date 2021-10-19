import logging

from urlstudy.pipeline import my_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

# fill the queue with jobs to run
if __name__ == '__main__':
    logging.info("Starting to run pipeline with {} stages".format(my_pipeline.stage_count()))
    my_pipeline.run()
