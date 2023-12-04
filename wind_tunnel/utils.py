"""Util functions for wind tunnel"""
import os
import shutil
import json

import inductiva


def simulate_wind_tunnel_scenario(obj_path, flow_velocity, x_geometry,
                                  y_geometry, z_geometry, num_iterations,
                                  machine_group, resolution):
    domain_geometry = {"x": x_geometry, "y": y_geometry, "z": z_geometry}

    scenario = inductiva.fluids.WindTunnel(flow_velocity=flow_velocity,
                                           domain=domain_geometry)

    task = scenario.simulate(object_path=obj_path,
                             num_iterations=num_iterations,
                             resolution=resolution,
                             machine_group=machine_group)
    return task


def make_machine_group(machine_type, num_machines, disk_size_gb,
                       elastic_machine_group):
    if elastic_machine_group:
        return inductiva.resources.ElasticMachineGroup(
            machine_type=machine_type,
            min_machines=1,
            max_machines=num_machines,
            disk_size_gb=disk_size_gb)
    return inductiva.resources.MachineGroup(machine_type=machine_type,
                                            num_machines=num_machines,
                                            disk_size_gb=disk_size_gb)


def copy_obj_files_and_metadata_to_output(obj_task_velocities, output_dataset):
    """Copy the obj files and metadata to the output dataset.

    Args:
        obj_task_velocities: List of tuples (object_path, task, flow_velocity).
        output_dataset: Path to the output dataset.
    """
    for object_path, task, flow_velocity in obj_task_velocities:
        os.makedirs(os.path.join(output_dataset, task.id))
        shutil.copy(object_path,
                    os.path.join(output_dataset, task.id, "object.obj"))

        # Save the flow velocity with the simulation.
        with open(os.path.join(output_dataset, task.id, "flow_velocity.json"),
                  "w",
                  encoding="utf-8") as f:
            json.dump(flow_velocity, f)
