import random
from datetime import datetime
import json
from tqdm import tqdm
import os
import windtunnel

# Constants
NUM_OBJECTS = 1
NUM_WIND_SPEED_VALUES = 4
NUM_ROTATION_VALUES = 5

MIN_WIND_SPEED = 10
MAX_WIND_SPEED = 50

NUM_ITERATIONS = 300
RESOLUTION = 5

MACHINE_GROUP_NAME = None

OBJ_DIR = 'data/output/instant-mesh-large/meshes_processed'
SUBMISSIONS_FILE = 'data/submissions/submissions.jsonl'

DEBUG = False


os.makedirs(os.path.dirname(SUBMISSIONS_FILE), exist_ok=True)

wind_tunnel = windtunnel.WindTunnel()

for i in tqdm(range(NUM_OBJECTS), desc="Processing Objects"):
    obj_file = os.path.join(OBJ_DIR, f"mesh_{i}.obj")

    rotation_angles = [int(random.uniform(0, 360)) for _ in range(NUM_ROTATION_VALUES - 2)]
    rotation_angles.extend([0, 180])

    wind_speeds = [int(random.uniform(MIN_WIND_SPEED, MAX_WIND_SPEED)) for _ in range(NUM_WIND_SPEED_VALUES)]

    for j in tqdm(range(NUM_WIND_SPEED_VALUES), desc="Processing different wind speeds"):
        for k in tqdm(range(NUM_ROTATION_VALUES), desc="Processing different rotation values"):
            data = {
                'wind_speed': wind_speeds[j % NUM_WIND_SPEED_VALUES],
                'rotate_angle': rotation_angles[k % NUM_ROTATION_VALUES],
                'num_iterations': NUM_ITERATIONS,
                'resolution': RESOLUTION,
            }

            submission_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            task = wind_tunnel.simulate(object_path=obj_file,
                                        wind_speed_ms=data['wind_speed'],
                                        rotate_z_degrees=data['rotate_angle'],
                                        num_iterations=data['num_iterations'],
                                        resolution=data['resolution'],
                                        display=DEBUG,
                                        machine_group_name=MACHINE_GROUP_NAME)
            
            task_data = {
                'task_id': task.id,
                'object_file': os.path.basename(obj_file),
                **data,
                'submission_time': submission_time
            }

            with open(SUBMISSIONS_FILE, 'a') as file:
                json.dump(task_data, file)
                file.write('\n')
