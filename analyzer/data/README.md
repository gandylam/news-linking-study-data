Static Data Files
=================

These were generated from the media cloud database. The `media-in-X.json` ones list an array of all the media sources
within the collection specified (see code below).

The `country-collections.json` was copied from the media cloud `front-end` repo, which has a script to generate it. 

## Generating Collection Media Files

```python
import mediacloud.api
KEY = 'sdfsdfdf'
mc = mediacloud.api.AdminMediaCloud(KEY)

# page through a list of media list results
def all_media_list(**kwargs):
    last_media_id = None
    more_results = True
    matching_media = []
    while more_results:
        media_page = mc.mediaList(**kwargs, last_media_id=last_media_id)
        print("  got a page of {} matching media".format(len(media_page)))
        if len(media_page) == 0:
            more_results = False
        else:
            matching_media += media_page
            last_media_id = media_page[-1]['media_id']
    return matching_media
    
collection_id = 34412234
media = all_media_list(tags_id=collection_id, rows=100)
with open("media-in-{}.json".format(collection_id), 'w') as f:
    json.dump(media, f)
```