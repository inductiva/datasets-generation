"""Script to help generate meshes using InstantMesh"""

import os
import re
import subprocess

from absl import app, flags, logging
import postprocess_mesh
from tqdm import tqdm

FLAGS = flags.FLAGS
flags.DEFINE_string("input_path", "data/cars196", "Path to the input data.")
flags.DEFINE_string("config_file", "configs/instant-mesh-large.yaml",
                    "Path to the config file.")
flags.DEFINE_string("output_path", "data/output",
                    "Path to the output directory.")
flags.DEFINE_string("output_subdir", "instant-mesh-large",
                    "Subdirectory for output.")
flags.DEFINE_bool("postprocess_meshes", True, "Post process meshes.")
flags.DEFINE_bool("debug", False, "Enable debug logging.")

COMMAND_TEMPLATE = ("python run.py {config} {input_file} --save_video "
                    "--output_path {output_path}")


def natural_sort_key(s):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r"(\d+)", s)
    ]


def generate_meshes():
    meshes_dir = os.path.join(FLAGS.output_path, FLAGS.output_subdir, "meshes")
    meshes_processed_dir = os.path.join(FLAGS.output_path, FLAGS.output_subdir,
                                        "meshes_processed")

    os.makedirs(meshes_processed_dir, exist_ok=True)

    files = os.listdir(FLAGS.input_path)
    image_files = sorted(
        [f for f in files if f.endswith(".jpg") or f.endswith(".png")],
        key=natural_sort_key,
    )

    for i, filename in tqdm(enumerate(image_files)):
        image_path = os.path.join(FLAGS.input_path, filename)
        filename_no_ext = os.path.splitext(filename)[0]
        obj_path = os.path.join(meshes_dir, f"{filename_no_ext}.obj")
        obj_path_renamed = os.path.join(meshes_dir, f"mesh_{i}.obj")
        processed_obj_path = os.path.join(meshes_processed_dir, f"mesh_{i}.obj")
        command = COMMAND_TEMPLATE.format(
            config=FLAGS.config_file,
            input_file=image_path,
            output_path=FLAGS.output_path,
        )

        try:
            subprocess.run(command, shell=True, check=True)
            os.rename(obj_path, obj_path_renamed)
            print(f"Successfully generated mesh_{i}.obj")

            if FLAGS.postprocess_meshes:
                postprocess_mesh.postprocess_mesh(obj_path, processed_obj_path)
                print(f"Successfully processed mesh_{i}.obj")

        except subprocess.CalledProcessError as e:
            print(f"Error occurred while processing {filename}: {e}")


def main(_):
    if FLAGS.debug:
        logging.set_verbosity(logging.DEBUG)
    else:
        logging.set_verbosity(logging.INFO)

    generate_meshes()


if __name__ == "__main__":
    app.run(main)
