import os
from prefect import Flow, Parameter
from prefect.executors import LocalDaskExecutor
import analyzer.tasks as tasks
import logging


logger = logging.getLogger()
INPUT_DIR = "input"

if __name__ == '__main__':

    with Flow("link-extraction") as flow:
        flow.executor = LocalDaskExecutor(scheduler="threads", num_workers=48)  # execute `map` calls in parallel
        # 1. list all the files we need to process
        input_dir = Parameter("input_dir", default="input")
        file_paths = tasks.list_json_files_in_dir(input_dir)
        # 2. extract links form files (in parallel)
        story_data = tasks.get_story_data.map(file_paths)
        # 3. write that out to a story list CSV
        link_csv_output_file = Parameter("story_csv_output_file", default="story-data.csv")
        tasks.write_story_csv(link_csv_output_file, story_data)
        # 4. extract links form files (in parallel)
        link_per_story = tasks.get_link_data_from_story.map(file_paths)
        # 5. save lists of links per media source
        link_csv_output_file = Parameter("link_csv_output_file", default="link-data.csv")
        link_ndjson_output_file = Parameter("link_ndjson_output_file", default="link-data.ndjson")
        tasks.write_link_file(link_csv_output_file, link_ndjson_output_file, link_per_story)

    # run our pipeline **for each media directory**
    media_dirs = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, f))]
    for media_dir in media_dirs:
        media_id = media_dir.split("/")[-1]
        story_csv_file = os.path.join("export", "stories-by-media", "{}-stories.csv".format(media_id))
        link_csv_file = os.path.join("export", "links-by-media", "csv", "{}-links.csv".format(media_id))
        link_ndjson_file = os.path.join("export", "links-by-media", "ndjson", "{}-links.ndjson".format(media_id))
        # for each media source that we haven't processed yet
        #if not (os.path.exists(csv_file) and os.path.exists(ndjson_file)):
        flow.run(parameters={
            'input_dir': media_dir,
            'story_csv_output_file': story_csv_file,
            'link_csv_output_file': link_csv_file,
            'link_ndjson_output_file': link_ndjson_file
        })
