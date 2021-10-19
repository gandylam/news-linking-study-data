import logging
from analyzer.database import get_mongo_collection
import copy

import analyzer.tasks as tasks

logger = logging.getLogger(__name__)


class Pipeline(object):

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._stage_names = []

    def add_stage(self, new_stage):
        self._stage_names.append(new_stage)

    def stage_count(self):
        return len(self._stage_names)

    def run(self, limit: int = None):
        for idx, stage in enumerate(self._stage_names):
            logger.info("  Stage {}: {}".format(idx, stage))
            story_count = 0
            for story in self._stories_for_stage(idx, limit):
                self._queue_story_for_stage(story, idx)
                story_count += 1
            logger.info("    {} stories to queue".format(story_count))

    def _stories_for_stage(self, idx: int, limit: int = None):
        raise NotImplementedError("Subclasses should implement this!")

    def _queue_story_for_stage(self, story, idx: int):
        raise NotImplementedError("Subclasses should implement this!")


class MongoPipeline(Pipeline):

    METADATA_KEY = "_pipeline"
    NEXT_STAGE_KEY = "next_stage"

    def __init__(self, uri: str, db_name: str, collection: str = 'stories'):
        super(MongoPipeline, self).__init__()
        self._collection = get_mongo_collection()

    def add_stage(self, stage_name: str):
        self._stage_names.append(stage_name)

    def _init_stories_with_metadata(self):
        # add some indexes to make searching faster
        self._collection.create_index(self.METADATA_KEY)
        self._collection.create_index(self.METADATA_KEY+"."+self.NEXT_STAGE_KEY)
        self._collection.create_index('stories_id')
        # now intiailize any records that don't have the pipeline metadata we need
        self._collection.update_many(
            {self.METADATA_KEY: {"$exists": False}},
            {'$set': {self.METADATA_KEY: {self.NEXT_STAGE_KEY: 0}}},
        )

    def _stories_for_stage(self, index: int, limit: int = None):
        self._init_stories_with_metadata()
        matching = self._collection.find({self.METADATA_KEY: {self.NEXT_STAGE_KEY: index}})
        if limit is not None:
            matching = matching.limit(limit)
        for story in matching:
            yield story

    def _queue_story_for_stage(self, story, idx: int):
        stage_name = self._stage_names[idx]
        del story['_id']  # can't be serialized and we don't need it
        tasks.run_stage.delay(idx, stage_name, copy.deepcopy(story))
