"""Resubmits tasks that failed

It assumes a .json file containing the simulation ids and other
simulation info:

{
    "task_ids": [
        "task_id_1",
        "task_id_2",
        ...
    ]
    "machine_group_machine_type": "n1-standard-4",
    "machine_group_num_machines": 1,
    "machine_group_disk_size_gb": 100,
    "x_geometry": [-5, 20],
    "y_geometry": [-5, 20],
    "z_geometry": [0, 8]

}

And a structure like this:

data/
simulation_info.json
task_id_1/
    object.obj
    flow_velocity.json
task_id_2/
    object.obj
    flow_velocity.json

Where flow_velocity.json is a file containing the flow velocity in a
list of 3 numbers, the x, y, z components of the flow

"""
import os
import shutil
import json

from absl import app
from absl import flags
from absl import logging

import inductiva

import utils

FLAGS = flags.FLAGS

flags.DEFINE_string('path_to_sim_info', None, 'Path to simulation info')


def get_failed_tasks(task_ids):
    """Returs ids of tasks that failed"""
    failed_tasks = []
    for task_id in task_ids:
        task = inductiva.tasks.Task(task_id)
        status = task.get_status()
        if status != "success":
            failed_tasks.append(task_id)
    return failed_tasks


def delete_from_disk_failed_tasks(parent_dir, task_ids):
    """Removes the folders of failed tasks"""
    for task_id in task_ids:
        path_to_task = os.path.join(parent_dir, task_id)
        shutil.rmtree(path_to_task)
        logging.info("Removed %s", path_to_task)


def remove_from_list_failed_task_ids(task_ids, failed_task_ids):
    """Removes failed tasks from list of task ids"""
    new_task_ids = []
    for task_id in task_ids:
        if task_id not in failed_task_ids:
            new_task_ids.append(task_id)
    return new_task_ids


def rewrite_json_file(path_to_json, failed_task_ids, new_tasks_ids):
    """Rewrites the json file with the new task ids"""
    with open(path_to_json, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    ids = json_data["task_ids"]
    ids = remove_from_list_failed_task_ids(ids, failed_task_ids)
    ids += new_tasks_ids
    json_data["task_ids"] = ids
    name, _ = os.path.splitext(os.path.basename(path_to_json))
    path = os.path.join(os.path.dirname(path_to_json),
                        name + "_after_resubmit.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_data, f)


def main(_):
    with open(FLAGS.path_to_sim_info, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    task_ids = json_data["task_ids"]
    machine_type = json_data["machine_group_machine_type"]
    num_machines = json_data["machine_group_num_machines"]
    disk_size_gb = json_data["machine_group_disk_size_gb"]
    machine_group_elastic = json_data["machine_group_elastic"]

    x_geometry = json_data["x_geometry"]
    y_geometry = json_data["y_geometry"]
    z_geometry = json_data["z_geometry"]

    num_iterations = json_data["num_iterations"]
    resolution = json_data["resolution"]

    failed_tasks = get_failed_tasks(task_ids)

    try:
        machine_group = utils.make_machine_group(machine_type, num_machines,
                                                 disk_size_gb,
                                                 machine_group_elastic)
        machine_group.start()

        parent_dir = os.path.dirname(FLAGS.path_to_sim_info)
        obj_task_velocities = []
        for task_id in failed_tasks:
            object_path = os.path.join(parent_dir, task_id, "object.obj")
            with open(os.path.join(parent_dir, task_id, "flow_velocity.json"),
                      "r",
                      encoding="utf-8") as f:
                flow_velocity = json.load(f)
            task = utils.simulate_wind_tunnel_scenario(
                object_path, flow_velocity, x_geometry, y_geometry, z_geometry,
                num_iterations, machine_group, resolution)
            obj_task_velocities.append((object_path, task, flow_velocity))

        utils.copy_obj_files_and_metadata_to_output(obj_task_velocities,
                                                    parent_dir)
        logging.info("Rewriting json file")
        rewrite_json_file(FLAGS.path_to_sim_info, failed_tasks,
                          [task.id for _, task, _ in obj_task_velocities])
        logging.info("Deleting failed tasks from disk")
        delete_from_disk_failed_tasks(parent_dir, failed_tasks)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Terminating machine group.")
        machine_group.terminate()
    # pylint: disable=broad-except
    except Exception as e:
        logging.error("Error occurred: %s", e)
        machine_group.terminate()


if __name__ == "__main__":
    app.run(main)
