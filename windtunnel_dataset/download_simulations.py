import json
import os

import inductiva
import windtunnel
from absl import app, flags, logging

FLAGS = flags.FLAGS
flags.DEFINE_boolean("debug", False, "Enable debug mode")


SUBMISSIONS_FILE = "submissions.jsonl"
DATA_FOLDER = "data"
INPUT_MESH_FILE = "input_mesh.obj"
OPENFOAM_MESH_FILE = "openfoam_mesh.obj"
PRESSURE_FIELD_MESH_FILE = "pressure_field_mesh.vtk"
STREAMLINES_MESH_FILE = "streamlines_mesh.ply"
SIMULATION_METADATA_FILE = "simulation_metadata.json"
FAILED_SIMULATIONS_FILE = "failed_simulations.json"


def download_task(task_id):
    task = inductiva.tasks.Task(task_id)
    task.wait()
    if task.is_failed():
        raise Exception("Task failed")
    output_dir = task.download_outputs()
    return output_dir


def postprocess_tasks(tasks_file):
    with open(tasks_file, "r") as file:
        for line in file:
            task_metadata = json.loads(line.strip())
            task_id = task_metadata.get("task_id")
            print(f"Processing task: {task_id}")
            object_number = (
                task_metadata.get("object_file").split("_")[-1].split(".")[0]
            )
            if int(object_number) < 700:
                split = "train"
            elif int(object_number) < 900:
                split = "val"
            else:
                split = "test"
            try:
                postprocess_task(task_id, task_metadata, split)
            except Exception as e:
                with open(FAILED_SIMULATIONS_FILE, "a") as f:
                    f.write(f"{task_id}\n")
                print(f"Failed to postprocess task {task_id}: {e}")
            break


def get_simulation_metadata(
    task_metadata,
    coeff,
    input_mesh_path,
    openfoam_mesh_path,
    pressure_field_mesh_path,
    streamlines_mesh_path,
):
    object_file = task_metadata.get("object_file").replace("image", "object")
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
    return simulation_metadata


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

    output_path = os.path.join(DATA_FOLDER, split, task_id)
    os.makedirs(output_path, exist_ok=True)

    input_mesh_path = os.path.join(output_path, INPUT_MESH_FILE)
    openfoam_mesh_path = os.path.join(output_path, OPENFOAM_MESH_FILE)
    pressure_field_mesh_path = os.path.join(output_path, PRESSURE_FIELD_MESH_FILE)
    streamlines_mesh_path = os.path.join(output_path, STREAMLINES_MESH_FILE)
    simulation_metadata_path = os.path.join(output_path, SIMULATION_METADATA_FILE)

    input_mesh.save(input_mesh_path)
    openfoam_mesh.save(openfoam_mesh_path)
    pressure_field_mesh.save(pressure_field_mesh_path)
    streamlines_mesh.save(streamlines_mesh_path)

    with open(simulation_metadata_path, "w", encoding="UTF-8") as f:
        simulation_metadata = get_simulation_metadata(
            task_metadata,
            coeff,
            input_mesh_path,
            openfoam_mesh_path,
            pressure_field_mesh_path,
            streamlines_mesh_path,
        )
        json.dump(simulation_metadata, f, indent=4)


def main(_):
    if FLAGS.debug:
        logging.set_verbosity(logging.DEBUG)

    postprocess_tasks(SUBMISSIONS_FILE)


if __name__ == "__main__":
    logging.set_verbosity(logging.INFO)
    app.run(main)
