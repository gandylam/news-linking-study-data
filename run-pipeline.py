import os
from prefect import Flow, Parameter
from prefect.executors import LocalDaskExecutor
import analyzer.tasks as tasks

INPUT_DIR = "input"

if __name__ == '__main__':

    with Flow("link-extraction") as flow:
        flow.executor = LocalDaskExecutor(scheduler="threads", num_workers=24)  # execute `map` calls in parallel
        # 1. list all the files we need to process
        input_dir = Parameter("input_dir", default="input")
        file_paths = tasks.list_json_files_in_dir(input_dir)
        # 2. process all the files (in parallel)
        link_per_story = tasks.get_link_data_from_story.map(file_paths)
        # 3. save results
        csv_output_file = Parameter("csv_output_file", default="data.csv")
        ndjson_output_file = Parameter("ndjson_output_file", default="data.ndjson")
        tasks.write_json_link_file(csv_output_file, ndjson_output_file, link_per_story)

    # run our pipeline for each media directory
    media_dirs = [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, f))]
    to_do = 0
    for media_dir in media_dirs:
        media_id = media_dir.split("/")[-1]
        csv_file = os.path.join("export", "links-by-media", "csv", "{}-links.csv".format(media_id))
        ndjson_file = os.path.join("export", "links-by-media", "ndjson", "{}-links.ndjson".format(media_id))
        # fun each media source that we haven't processed yet
        if not (os.path.exists(csv_file) and os.path.exists(ndjson_file)):
            to_do += 1
            flow.run(parameters={
                'input_dir': media_dir,
                'csv_output_file': csv_file,
                'ndjson_output_file': ndjson_file
            })
