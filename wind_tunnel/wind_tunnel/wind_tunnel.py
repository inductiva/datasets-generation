'''Hugging face loading script

Hugging face loading script for the wind tunnel data. This script
assumes that the data is stored on the google cloud bucket
'gs://wind_tunnel_data/' where several datasets can be stored in zipp
format. For example:

gs://wind_tunnel_data/
├── v0.1.zip
├── v0.2.zip
└── v0.3.zip

Each zip file should have the structure:

v0.1.zip
└── v0.1
    ├── 102042348
    │   ├── edges.npy
    │   ├── nodes.npy
    │   ├── wind_pressures.npy
    │   └── wind_velocities.npy
    ├── 102042349
    │   ├── edges.npy
    │   ├── nodes.npy
    │   ├── wind_pressures.npy
    │   └── wind_velocities.npy
    ├── 102042350
    │   ├── edges.npy
    │   ├── nodes.npy
    │   ├── wind_pressures.npy
    │   └── wind_velocities.npy

Where each subdirectory corresponds to a different simulation.

To load the data, use the following code:

from datasets import load_dataset
dataset = load_dataset('wind_tunnel', 'v0.1')

'''
import os

import datasets
import numpy as np

_DESCRIPTION = 'Wind tunnel dataset example.'

_BASE_URL = 'gs://wind_tunnel_data/'

_DEFAULT_FLOW_VELOCITY = [0, 0, 0]


class WindTunnel(datasets.GeneratorBasedBuilder):
    '''Wind tunnel builder'''

    def __init__(self, version, **kwargs):
        '''BuilderConfig for WindTunnel.

        Args:
            version: `string`, version of the dataset to use.
        '''
        super(WindTunnel, self).__init__(**kwargs)
        self.version = version
        self.bucket_url = _BASE_URL + f'{version}.zip'

    def _info(self):
        return datasets.DatasetInfo(description=_DESCRIPTION,
                                    features=datasets.Features({
                                        'nodes':
                                        datasets.Array2D((None, 3),
                                                         dtype='float32'),
                                        'edges':
                                        datasets.Array2D((None, 2),
                                                         dtype='int32'),
                                        'flow_velocity':
                                        [datasets.Value('float32')],
                                        'wind_pressures':
                                        [datasets.Value('float32')]
                                    }))

    def _split_generators(self, dl_manager):
        # Download and extract the zip file in the bucket.
        downloaded_dir = dl_manager.download_and_extract(self.bucket_url)

        dirs = [
            os.path.join(downloaded_dir, self.version, dir_)
            for dir_ in os.listdir(os.path.join(downloaded_dir, self.version))
        ]

        return [
            datasets.SplitGenerator(name=datasets.Split.TRAIN,
                                    gen_kwargs={'sim_dir_paths': dirs})
        ]

    # pylint: disable=arguments-differ
    def _generate_examples(self, sim_dir_paths):
        for id_, sim_dir_path in enumerate(sim_dir_paths):
            nodes = np.load(os.path.join(sim_dir_path, 'nodes.npy'))
            edges = np.load(os.path.join(sim_dir_path, 'edges.npy'))
            wind_pressures = np.load(
                os.path.join(sim_dir_path, 'wind_pressures.npy'))

            flow_velocity_path = os.path.join(sim_dir_path,
                                              'flow_velocities.npy')
            if os.path.exists(flow_velocity_path):
                flow_velocity = np.load(flow_velocity_path)
            else:
                flow_velocity = _DEFAULT_FLOW_VELOCITY

            yield id_, {
                'nodes': nodes,
                'edges': edges,
                'flow_velocity': flow_velocity,
                'wind_pressures': wind_pressures,
            }
