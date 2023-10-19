"""Estimates the costs of tasks based on example simulations.

Assumes the existence of a json file with the following structure:

{
    "task_ids": [
        "task_id_1",
        "task_id_2",
        ...
    ],
    "machine_group_machine_type": "n1-standard-4",
    "machine_group_num_machines": 1,
    "machine_group_disk_size_gb": 100
}

"""
import json

from absl import app
from absl import flags
from absl import logging

import inductiva

import common

FLAGS = flags.FLAGS

flags.DEFINE_string("path_to_sim_info", None,
                    "The path to the simulation info json file.")


# TODO(augusto): As the scripts grow we can move these functions to a
# utils.py file
def get_tasks_duration(tasks):
    """Gets the duration of the tasks in seconds"""
    durations = []
    for task in tasks:
        durations.append(task.get_execution_time())
    return durations


def main(_):
    # Read the simulation ids
    with open(FLAGS.path_to_sim_info, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    task_ids = json_data["task_ids"]
    machine_type = json_data["machine_group_machine_type"]
    num_machines = json_data["machine_group_num_machines"]
    disk_size = json_data["machine_group_disk_size_gb"]

    tasks_successfully_completed = common.get_successfull_tasks(task_ids)

    if not tasks_successfully_completed:
        logging.error("Not enough information to perform the task.")
        return

    durations = get_tasks_duration(tasks_successfully_completed)

    machine_group = inductiva.resources.MachineGroup(machine_type=machine_type,
                                                     num_machines=num_machines,
                                                     disk_size_gb=disk_size)

    price_per_hour = machine_group.estimate_cloud_cost()

    average_sim_duration = sum(durations) / len(durations)
    logging.info("Average simulation duration: %s seconds",
                 average_sim_duration)

    average_task_cost = average_sim_duration * price_per_hour / 3600
    logging.info("Average simulation cost: %s USD", average_task_cost)


if __name__ == "__main__":
    app.run(main)
