import logging

from analyzer.database import get_mongo_collection
import analyzer.stages
import analyzer.pipeline as pipeline
from analyzer.celery import app

logger = logging.getLogger(__name__)  # get_task_logger(__name__)


@app.task(serializer='json', bind=True)
def run_stage(self, index, stage_name, story):
    StageClass = _get_stage_by_name(stage_name)
    stage = StageClass()
    results = stage.process(story)
    # and save results to db
    collection = get_mongo_collection()
    collection.update_one({'stories_id': story['stories_id']}, {'$set': results})
    # and set it up for the next stage
    new_metadata = dict()
    new_metadata[pipeline.MongoPipeline.METADATA_KEY] = {}
    new_metadata[pipeline.MongoPipeline.METADATA_KEY][pipeline.MongoPipeline.NEXT_STAGE_KEY] = index+1
    collection.update_one({'stories_id': story['stories_id']}, {'$set': new_metadata})
    # and tell the user
    logging.debug("Story {}: {} -> {}".format(story['stories_id'], index, index+1))


def _get_stage_by_name(stage_name: str) -> object:
    return getattr(analyzer.stages, stage_name)
