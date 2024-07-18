"""Script to help generate meshes using InstantMesh"""

import os
import re
import subprocess

from preprocess_meshes import preprocess_mesh
from tqdm import tqdm

# Constants
INPUT_PATH = 'data/cars196'
CONFIG_FILE = 'configs/instant-mesh-large.yaml'
OUTPUT_PATH = 'data/output'
OUTPUT_SUBDIR = 'instant-mesh-large'
MESHES_DIR = os.path.join(OUTPUT_PATH, OUTPUT_SUBDIR, 'meshes')
MESHES_PROCESSED_DIR = os.path.join(OUTPUT_PATH, OUTPUT_SUBDIR,
                                    'meshes_processed')
COMMAND_TEMPLATE = ('python run.py {config} {input_file} --save_video '
                    '--output_path {output_path}')
PREPROCESS_ENABLED = True


def natural_sort_key(s):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r'(\d+)', s)
    ]


def generate_meshes(input_path, config_file):
    files = os.listdir(input_path)
    image_files = sorted(
        [f for f in files if f.endswith('.jpg') or f.endswith('.png')],
        key=natural_sort_key)

    for i, filename in tqdm(enumerate(image_files)):
        image_path = os.path.join(input_path, filename)
        filename_no_ext = os.path.splitext(filename)[0]
        obj_path = os.path.join(MESHES_DIR, f"{filename_no_ext}.obj")
        obj_path_renamed = os.path.join(MESHES_DIR, f"mesh_{i}.obj")
        processed_obj_path = os.path.join(MESHES_PROCESSED_DIR, f"mesh_{i}.obj")
        command = COMMAND_TEMPLATE.format(config=config_file,
                                          input_file=image_path,
                                          output_path=OUTPUT_PATH)

        try:
            subprocess.run(command, shell=True, check=True)
            os.rename(obj_path, obj_path_renamed)
            print(f"Successfully generated mesh_{i}.obj")

            if PREPROCESS_ENABLED:
                preprocess_mesh(obj_path, processed_obj_path)
                print(f"Successfully processed mesh_{i}.obj")

        except subprocess.CalledProcessError as e:
            print(f"Error occurred while processing {filename}: {e}")


if __name__ == '__main__':
    os.makedirs(MESHES_PROCESSED_DIR, exist_ok=True)
    generate_meshes(INPUT_PATH, CONFIG_FILE)
