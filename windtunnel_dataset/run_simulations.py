""" Run simulations for the wind tunnel dataset. """

import json
import os
from datetime import datetime

import windtunnel
from absl import app, flags, logging
from tqdm import tqdm

FLAGS = flags.FLAGS

flags.DEFINE_integer('NUM_ITERATIONS', 300, 'Number of iterations')
flags.DEFINE_integer('RESOLUTION', 5, 'Resolution')

flags.DEFINE_string('MACHINE_GROUP_NAME', None, 'Machine group name')
flags.DEFINE_string('SUBMISSIONS_FILE', 'data/submissions.jsonl',
                    'Submissions file')
flags.DEFINE_string('PARAMS_FILE', 'data/params.json', 'Parameters file')

flags.DEFINE_boolean('DEBUG', False, 'Debug mode')


def load_parameters():
    with open(FLAGS.PARAMS_FILE, 'r', encoding='utf-8') as file:
        params = json.load(file)
    return params


def run_simulations(params):
    wind_tunnel = windtunnel.WindTunnel()

    for param in tqdm(params, desc='Processing Simulations'):
        data = {
            'wind_speed': param['wind_speed'],
            'rotate_angle': param['rotation_angle'],
            'num_iterations': FLAGS.NUM_ITERATIONS,
            'resolution': FLAGS.RESOLUTION,
        }

        submission_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        task = wind_tunnel.simulate(object_path=param['object_path'],
                                    wind_speed_ms=data['wind_speed'],
                                    rotate_z_degrees=data['rotate_angle'],
                                    num_iterations=data['num_iterations'],
                                    resolution=data['resolution'],
                                    display=FLAGS.DEBUG,
                                    machine_group_name=FLAGS.MACHINE_GROUP_NAME)

        task_data = {
            'task_id': task.id,
            'object_file': os.path.basename(param['object_path']),
            **data, 'submission_time': submission_time
        }

        with open(FLAGS.SUBMISSIONS_FILE, 'a', encoding='utf-8') as file:
            json.dump(task_data, file)
            file.write('\n')


def main(_):
    params = load_parameters()
    run_simulations(params)


if __name__ == '__main__':
    logging.set_verbosity(logging.INFO)
    app.run(main)
