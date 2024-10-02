"""Download and postprocess WindTunnel simulations."""

import json
import os

import inductiva
import windtunnel
from absl import app, flags, logging

FLAGS = flags.FLAGS
flags.DEFINE_boolean("debug", False, "Enable debug mode")
flags.DEFINE_string("submissions_file", "submissions.jsonl",
                    "Path to the submissions file.")
flags.DEFINE_string("data_folder", "data", "Path to the data folder.")
flags.DEFINE_string("input_mesh_file", "input_mesh.obj",
                    "Name of the input mesh file.")
flags.DEFINE_string("openfoam_mesh_file", "openfoam_mesh.obj",
                    "Name of the OpenFOAM mesh file.")
flags.DEFINE_string(
    "pressure_field_mesh_file",
    "pressure_field_mesh.vtk",
    "Name of the pressure field mesh file.",
)
flags.DEFINE_string(
    "streamlines_mesh_file",
    "streamlines_mesh.ply",
    "Name of the streamlines mesh file.",
)
flags.DEFINE_string(
    "simulation_metadata_file",
    "simulation_metadata.json",
    "Path to the simulation metadata file.",
)
flags.DEFINE_string(
    "failed_simulations_file",
    "failed_simulations.json",
    "Path to the failed simulations file.",
)


def download_task(task_id):
    task = inductiva.tasks.Task(task_id)
    task.wait()
    if task.is_failed():
        raise Exception("Task failed")
    output_dir = task.download_outputs()
    return output_dir


def postprocess_tasks():
    with open(FLAGS.submissions_file, "r", encoding="utf-8") as file:
        for line in file:
            task_metadata = json.loads(line.strip())
            task_id = task_metadata.get("task_id")
            print(f"Processing task: {task_id}")
            object_number = (
                task_metadata.get("object_file").split("_")[-1].split(".")[0])
            if int(object_number) < 700:
                split = "train"
            elif int(object_number) < 900:
                split = "val"
            else:
                split = "test"
            try:
                postprocess_task(task_id, task_metadata, split)
            except Exception as e:
                with open(FLAGS.failed_simulations_file, "a",
                          encoding="utf-8") as f:
                    f.write(f"{task_id}\n")
                print(f"Failed to postprocess task {task_id}: {e}")
            break


def postprocess_task(task_id, task_metadata, split):
    output_dir = download_task(task_id)
    if output_dir is None:
        return
    outputs = windtunnel.WindTunnelOutputs(output_dir)

    coeff = outputs.get_force_coefficients()
    input_mesh = outputs.get_input_mesh()
    openfoam_mesh = outputs.get_openfoam_object_mesh()
    pressure_field_mesh = outputs.get_interpolated_pressure_field()
    streamlines_mesh = outputs.get_streamlines()

    output_path = os.path.join(FLAGS.data_folder, split, task_id)
    os.makedirs(output_path, exist_ok=True)

    input_mesh_path = os.path.join(output_path, FLAGS.input_mesh_file)
    openfoam_mesh_path = os.path.join(output_path, FLAGS.openfoam_mesh_file)
    pressure_field_mesh_path = os.path.join(output_path,
                                            FLAGS.pressure_field_mesh_file)
    streamlines_mesh_path = os.path.join(output_path,
                                         FLAGS.streamlines_mesh_file)
    simulation_metadata_path = os.path.join(output_path,
                                            FLAGS.simulation_metadata_file)

    input_mesh.save(input_mesh_path)
    openfoam_mesh.save(openfoam_mesh_path)
    pressure_field_mesh.save(pressure_field_mesh_path)
    streamlines_mesh.save(streamlines_mesh_path)

    object_file = task_metadata.get("object_file").replace("image", "object")

    with open(simulation_metadata_path, "w", encoding="UTF-8") as f:
        simulation_metadata = {
            "id": task_metadata.get("task_id"),
            "object_file": object_file,
            "wind_speed": task_metadata.get("wind_speed"),
            "rotate_angle": task_metadata.get("rotate_angle"),
            "num_iterations": task_metadata.get("num_iterations"),
            "resolution": task_metadata.get("resolution"),
            "drag_coefficient": coeff.get("Drag"),
            "moment_coefficient": coeff.get("Moment"),
            "lift_coefficient": coeff.get("Lift"),
            "front_lift_coefficient": coeff.get("Front Lift"),
            "rear_lift_coefficient": coeff.get("Rear Lift"),
            "input_mesh_path": input_mesh_path,
            "openfoam_mesh_path": openfoam_mesh_path,
            "pressure_field_mesh_path": pressure_field_mesh_path,
            "streamlines_mesh_path": streamlines_mesh_path,
        }
        json.dump(simulation_metadata, f, indent=4)


def main(_):
    if FLAGS.debug:
        logging.set_verbosity(logging.DEBUG)

    postprocess_tasks()


if __name__ == "__main__":
    logging.set_verbosity(logging.INFO)
    app.run(main)
