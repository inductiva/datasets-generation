"""
Run the simulation for the given number of objects, wind speeds,
and rotation values
"""

import json
import os
import random
from datetime import datetime

import windtunnel
from absl import app, flags, logging
from tqdm import tqdm

FLAGS = flags.FLAGS
flags.DEFINE_integer('NUM_OBJECTS', 100, 'Number of objects')
flags.DEFINE_integer('NUM_WIND_SPEED_VALUES', 4, 'Number of wind speed values')
flags.DEFINE_integer('NUM_ROTATION_VALUES', 5, 'Number of rotation values')

flags.DEFINE_integer('MIN_WIND_SPEED', 10, 'Minimum wind speed')
flags.DEFINE_integer('MAX_WIND_SPEED', 50, 'Maximum wind speed')

flags.DEFINE_integer('NUM_ITERATIONS', 300, 'Number of iterations')
flags.DEFINE_integer('RESOLUTION', 5, 'Resolution')

flags.DEFINE_string('MACHINE_GROUP_NAME', None, 'Machine group name')

flags.DEFINE_string('OBJ_DIR',
                    'data/output/instant-mesh-large/meshes_processed',
                    'Object directory')
flags.DEFINE_string('SUBMISSIONS_FILE', 'data/submissions/submissions.jsonl',
                    'Submissions file')

flags.DEFINE_boolean('DEBUG', False, 'Debug mode')

os.makedirs(os.path.dirname(FLAGS.SUBMISSIONS_FILE), exist_ok=True)


def main(_):

    wind_tunnel = windtunnel.WindTunnel()

    for i in tqdm(range(FLAGS.NUM_OBJECTS), desc='Processing Objects'):
        obj_file = os.path.join(FLAGS.OBJ_DIR, f'mesh_{i}.obj')

        rotation_angles = [
            int(random.uniform(0, 360))
            for _ in range(FLAGS.NUM_ROTATION_VALUES - 2)
        ]
        rotation_angles.extend([0, 180])

        wind_speeds = [
            int(random.uniform(FLAGS.MIN_WIND_SPEED, FLAGS.MAX_WIND_SPEED))
            for _ in range(FLAGS.NUM_WIND_SPEED_VALUES)
        ]

        for j in tqdm(range(FLAGS.NUM_WIND_SPEED_VALUES),
                      desc='Processing different wind speeds'):
            for k in tqdm(range(FLAGS.NUM_ROTATION_VALUES),
                          desc='Processing different rotation values'):
                data = {
                    'wind_speed':
                        wind_speeds[j % FLAGS.NUM_WIND_SPEED_VALUES],
                    'rotate_angle':
                        rotation_angles[k % FLAGS.NUM_ROTATION_VALUES],
                    'num_iterations':
                        FLAGS.NUM_ITERATIONS,
                    'resolution':
                        FLAGS.RESOLUTION,
                }

                submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                task = wind_tunnel.simulate(
                    object_path=obj_file,
                    wind_speed_ms=data['wind_speed'],
                    rotate_z_degrees=data['rotate_angle'],
                    num_iterations=data['num_iterations'],
                    resolution=data['resolution'],
                    display=FLAGS.DEBUG,
                    machine_group_name=FLAGS.MACHINE_GROUP_NAME)

                task_data = {
                    'task_id': task.id,
                    'object_file': os.path.basename(obj_file),
                    **data, 'submission_time': submission_time
                }

                with open(FLAGS.SUBMISSIONS_FILE, 'a',
                          encoding='utf-8') as file:
                    json.dump(task_data, file)
                    file.write('\n')


if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    app.run(main)
