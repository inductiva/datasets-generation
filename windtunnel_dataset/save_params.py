""" Generate parameters for the dataset. """

import json
import os
import random

from absl import app, flags, logging

FLAGS = flags.FLAGS
flags.DEFINE_integer('NUM_OBJECTS', 100, 'Number of objects')
flags.DEFINE_integer('NUM_WIND_SPEED_VALUES', 4, 'Number of wind speed values')
flags.DEFINE_integer('NUM_ROTATION_VALUES', 5, 'Number of rotation values')

flags.DEFINE_integer('MIN_WIND_SPEED', 10, 'Minimum wind speed')
flags.DEFINE_integer('MAX_WIND_SPEED', 50, 'Maximum wind speed')

flags.DEFINE_string('OBJ_DIR',
                    'data/output/instant-mesh-large/meshes_processed',
                    'Object directory')
flags.DEFINE_string('PARAMS_FILE', 'params.json', 'Parameters file')


def generate_parameters():
    rotation_angles = [
        int(random.uniform(0, 360))
        for _ in range(FLAGS.NUM_ROTATION_VALUES - 2)
    ]
    rotation_angles.extend([0, 180])

    wind_speeds = [
        int(random.uniform(FLAGS.MIN_WIND_SPEED, FLAGS.MAX_WIND_SPEED))
        for _ in range(FLAGS.NUM_WIND_SPEED_VALUES)
    ]

    return rotation_angles, wind_speeds


def save_parameters():
    obj_files = [
        os.path.join(FLAGS.OBJ_DIR, f'mesh_{i}.obj')
        for i in range(FLAGS.NUM_OBJECTS)
    ]

    params = []
    for obj_file in obj_files:
        rotation_angles, wind_speeds = generate_parameters()
        for wind_speed in wind_speeds:
            for rotation_angle in rotation_angles:
                params.append({
                    'object_path': obj_file,
                    'rotation_angle': rotation_angle,
                    'wind_speed': wind_speed
                })

    with open(FLAGS.PARAMS_FILE, 'w', encoding='utf-8') as file:
        json.dump(params, file, indent=4)


def main(_):
    save_parameters()


if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    app.run(main)
