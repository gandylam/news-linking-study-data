from mediacloud.storage import MongoStoryDatabase
import os
import ndjson
import json
import logging
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

EXPORT_FILE = os.path.join('export', 'story-links-sample1.ndjson')

# fill the queue with jobs to run
if __name__ == '__main__':
    db = MongoStoryDatabase()
    db.selectDatabase('url-linking')
    story_count = db.storyCount({"_pipeline": {"next_stage": 7}})
    logging.info("Exporting {} stories".format(story_count))
    # now write it all
    with io.open(EXPORT_FILE, 'w', encoding='utf8') as f:
        for story in db._db.stories.find({"_pipeline": {"next_stage": 7}}):
            #ndjson.dump(story['links'], f)
            if len(story['links']) > 0:
                f.write(json.dumps(story['links'], ensure_ascii=False)+"\n")
