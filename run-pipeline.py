import logging
import os
from prefect import Flow, Parameter
from prefect.executors import LocalDaskExecutor
import analyzer.tasks as tasks

#logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
#logger = logging.getLogger(__name__)
# silence the "ruthless removal did not work" INFO logs
#readability_logger = logging.getLogger('readability.readability')
#readability_logger.propagate = False

INPUT_DIR = "input"

if __name__ == '__main__':
    #logger.info("Reading input files from {}/".format(INPUT_DIR))

    with Flow("link-extraction") as flow:
        flow.executor = LocalDaskExecutor(scheduler="threads", num_workers=8) # execute `map` calls in parallel
        # 1. list all the files we need to process
        input_dir = Parameter("input_dir", default="input")
        file_paths = tasks.list_json_files_in_dir(input_dir)
        # 2. process all the files (in parallel)
        link_per_story = tasks.get_link_data_from_story.map(file_paths)
        # 3. save results
        output_file = Parameter("output_file", default="data.json")
        tasks.write_json_link_file(output_file, link_per_story)
    #flow.register(project_name="global-linking-study")

    # run our pipiline for each media directory
    media_dirs = [os.path.join(INPUT_DIR, f) for f in os.listdir("input") if os.path.isdir(os.path.join(INPUT_DIR, f))]
    #logger.info("Found {} media dirs to process".format(len(media_dirs)))
    for media_dir in media_dirs:
        #logger.info("  Running {}".format(media_dir))
        media_id = media_dir.split("/")[-1]
        output_file = os.path.join("export", "links-by-media", "{}-links".format(media_id))
        #logger.info("    will write results to {}".format(output_file))
        flow.run(parameters={'input_dir': media_dir, 'output_file': output_file})
