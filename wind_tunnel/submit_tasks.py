"""This file uses the inductiva API to sumbit tasks"""
import os
import json

from absl import app
from absl import flags
from absl import logging

import numpy as np

import utils

FLAGS = flags.FLAGS

flags.DEFINE_string("input_dataset", None, "Path to the dataset of objects.")

flags.DEFINE_list("flow_velocity_range_x", None,
                  "Range of flow velocity in the x-direction.")
flags.DEFINE_list("flow_velocity_range_y", None,
                  "Range of flow velocity in the y-direction.")
flags.DEFINE_list("flow_velocity_range_z", None,
                  "Range of flow velocity in the z-direction.")
flags.DEFINE_integer("num_simulations_per_object", 1,
                     "Number of simulations to run for each object.")
flags.DEFINE_boolean(
    "random_velocity", False,
    "Split the velocity range into num_simulations_per_object.")
flags.DEFINE_list("x_geometry", [-5, 20], "X geometry of the domain.")
flags.DEFINE_list("y_geometry", [-5, 5], "Y geometry of the domain.")
flags.DEFINE_list("z_geometry", [0, 8], "Z geometry of the domain.")
flags.DEFINE_integer("num_iterations", 100, "Number of iterations to run.")
flags.DEFINE_enum("resolution", "low", ["low", "medium", "high"],
                  "Resolution of the OpenFOAM meshes.")

flags.DEFINE_string("machine_type", "c2-standard-16", "Machine type.")
flags.DEFINE_integer("num_machines", 1, "Number of machines.")
flags.DEFINE_integer("disk_size_gb", 60, "Disk size in GB.")
flags.DEFINE_boolean("elastic_machine_group", True,
                     "Whether to use an elastic machine group.")

flags.DEFINE_string("output_dataset", None, "Path to the output dataset.")

flags.mark_flag_as_required("input_dataset")
flags.mark_flag_as_required("output_dataset")
flags.mark_flag_as_required("flow_velocity_range_x")
flags.mark_flag_as_required("flow_velocity_range_y")
flags.mark_flag_as_required("flow_velocity_range_z")


def make_velocities(vel_range_x, vel_range_y, vel_range_z, num_simulations,
                    random):
    generator = np.random.uniform if random else np.linspace
    return np.c_[generator(vel_range_x[0], vel_range_x[1], num_simulations),
                 generator(vel_range_y[0], vel_range_y[1], num_simulations),
                 generator(vel_range_z[0], vel_range_z[1], num_simulations)]


def main(_):
    object_paths = [
        os.path.join(FLAGS.input_dataset, path)
        for path in os.listdir(FLAGS.input_dataset)
    ]

    flow_velocity_range_x = list(map(float, FLAGS.flow_velocity_range_x))
    flow_velocity_range_y = list(map(float, FLAGS.flow_velocity_range_y))
    flow_velocity_range_z = list(map(float, FLAGS.flow_velocity_range_z))

    x_geometry = list(map(float, FLAGS.x_geometry))
    y_geometry = list(map(float, FLAGS.y_geometry))
    z_geometry = list(map(float, FLAGS.z_geometry))

    try:
        # Start the machine group with the requested parameters
        machine_group = utils.make_machine_group(FLAGS.machine_type,
                                                 FLAGS.num_machines,
                                                 FLAGS.disk_size_gb,
                                                 FLAGS.elastic_machine_group)
        machine_group.start()

        obj_task_velocities = []
        for object_path in object_paths:
            velocities = make_velocities(flow_velocity_range_x,
                                         flow_velocity_range_y,
                                         flow_velocity_range_z,
                                         FLAGS.num_simulations_per_object,
                                         FLAGS.random_velocity)
            for vel in velocities:
                task = utils.simulate_wind_tunnel_scenario(
                    object_path, vel, x_geometry, y_geometry, z_geometry,
                    FLAGS.num_iterations, machine_group, FLAGS.resolution)

                obj_task_velocities.append((object_path, task, vel.tolist()))

        utils.copy_obj_files_and_metadata_to_output(obj_task_velocities,
                                                    FLAGS.output_dataset)

        # Make a json with the task ids and the machine group name.
        with open(os.path.join(FLAGS.output_dataset, "sim_info.json"),
                  "w",
                  encoding="utf-8") as f:
            dict_to_save = {
                "task_ids": [task.id for _, task, _ in obj_task_velocities],
                "machine_group": machine_group.name,
                "machine_group_machine_type": FLAGS.machine_type,
                "machine_group_num_machines": FLAGS.num_machines,
                "machine_group_disk_size_gb": FLAGS.disk_size_gb,
                "machine_group_elastic": FLAGS.elastic_machine_group,
                "num_iterations": FLAGS.num_iterations,
                "x_geometry": x_geometry,
                "y_geometry": y_geometry,
                "z_geometry": z_geometry,
                "resolution": FLAGS.resolution
            }
            json.dump(dict_to_save, f)

    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Terminating machine group.")
        machine_group.terminate()
    # pylint: disable=broad-except
    except Exception as e:
        logging.error("Error occurred: %s", e)
        machine_group.terminate()


if __name__ == "__main__":
    app.run(main)
