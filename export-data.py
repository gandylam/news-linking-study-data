from mediacloud.storage import MongoStoryDatabase
import os
import json
import logging
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

EXPORT_FILE = os.path.join('export', 'story-links.ndjson')

# fill the queue with jobs to run
if __name__ == '__main__':
    db = MongoStoryDatabase()
    db.selectDatabase('url-linking')
    story_count = db.storyCount({"_pipeline": {"next_stage": 7}})
    logging.info("Exporting {} stories".format(story_count))
    # now write it all
    with io.open(EXPORT_FILE, 'w', encoding='utf8') as f:
        for story in db._db.stories.find({"_pipeline": {"next_stage": 7}}):
            for link in story['links']:
                link['publication_date'] = link['publication_date'][0:19]  # strip off milliseconds
                f.write(json.dumps(link, ensure_ascii=False)+"\n")
