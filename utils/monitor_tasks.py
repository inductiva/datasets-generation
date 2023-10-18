"""This script is responsible for monitoring tasks.

It assumes that the tasks ids are stored in a json file. The json file
should have the following format:

{
    "task_ids": [
        "task_id_1",
        "task_id_2",
        ...
    ],
    "machine_group": "machine_group_name"
}

The script also allows to terminate the machine group when all tasks
are done.

"""
import json

from absl import app
from absl import flags
from absl import logging

import inductiva

FLAGS = flags.FLAGS

flags.DEFINE_string("path_to_sim_info", None,
                    "The path to the simulation info json file.")

flags.DEFINE_bool("terminate_when_done", True,
                  "Terminates the machine group when no tasks are running.")

flags.DEFINE_bool("force_terminate", False,
                  "Force terminate the machine group.")


def main(_):
    # Read the simulation ids
    with open(FLAGS.path_to_sim_info, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    task_ids = json_data["task_ids"]
    machine_group_name = json_data["machine_group"]

    logging.info("Number of tasks: %s", len(task_ids))

    task_counts = {
        "success": 0,
        "submited": 0,
        "started": 0,
        "failed": 0,
        "killed": 0,
    }

    og_keys = set(task_counts.keys())

    for task_id in task_ids:
        task = inductiva.tasks.Task(task_id)
        status = task.get_status()
        if status not in task_counts:
            task_counts[status] = 0
        else:
            task_counts[status] += 1

    other_tasks = sum(
        [task_counts[key] for key in set(task_counts.keys()) - og_keys])

    logging.info("Tasks still running: %s",
                 task_counts["submited"] + task_counts["started"])
    logging.info("Tasks successfully completed: %s", task_counts["success"])
    logging.info("Tasks failed: %s", task_counts["failed"])
    logging.info("Tasks killed: %s", task_counts["killed"])
    logging.info("Other tasks: %s", other_tasks)

    if (task_counts["submited"] + task_counts["started"] == 0 and
            FLAGS.terminate_when_done) or FLAGS.force_terminate:
        machine_groups = inductiva.resources.machine_groups.get()
        for machine_group in machine_groups:
            if machine_group.name == machine_group_name:
                machine_group.terminate()
                logging.info("Machine group %s deleted.", machine_group_name)
                break


if __name__ == "__main__":
    app.run(main)
