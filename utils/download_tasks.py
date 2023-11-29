"""This file downloads the requested tasks.

It assumes a .json file containing the simulation ids of the tasks to download:

{
    "task_ids": [
        "task_id_1",
        "task_id_2",
        ...
    ]
}

And a structure like this:

data/
simulation_info.json
task_id_1/
    output_file_1
    output_file_2
    ...
task_id_2/
    output_file_1
    output_file_2
    ...
...

The output files are downloaded to the corresponding task_id folder.
"""
import json
import os

from absl import app
from absl import flags
from absl import logging

import utils

import inductiva

FLAGS = flags.FLAGS

flags.DEFINE_string("path_to_sim_info", None,
                    "The path to the simulation json info files.")

flags.DEFINE_list("files_to_download", None,
                  "The names of the output files to download.")

flags.mark_flag_as_required("files_to_download")


def main(_):
    # Read the simulation ids
    with open(FLAGS.path_to_sim_info, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    task_ids = json_data["task_ids"]

    logging.info("Number of tasks: %s", len(task_ids))

    tasks_ids_successfully_completed = utils.get_successfull_tasks(task_ids)
    logging.info("Tasks successfully completed: %s",
                 len(tasks_ids_successfully_completed))

    download_dir = os.path.dirname(FLAGS.path_to_sim_info)
    for task_id in tasks_ids_successfully_completed:
        save_path = os.path.join(download_dir, task_id)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        task = inductiva.tasks.Task(task_id)
        task.download_outputs(FLAGS.files_to_download, output_dir=save_path)


if __name__ == "__main__":
    app.run(main)
