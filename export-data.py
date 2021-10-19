from mediacloud.storage import MongoStoryDatabase
import ndjson
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

# fill the queue with jobs to run
if __name__ == '__main__':
    db = MongoStoryDatabase()
    db.selectDatabase('url-linking')
    story_count = db.storyCount({"_pipeline": {"next_stage": 7}})
    logging.info("Exporting {} stories".format(story_count))
    # now write it all
    with open('story-links-sample1.ndjson', 'w') as f:
        for story in db._db.stories.find({"_pipeline": {"next_stage": 7}}):
            ndjson.dump(story['links'], f)
