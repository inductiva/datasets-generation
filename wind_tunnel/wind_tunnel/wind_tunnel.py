'''Hugging face loading script

Hugging face loading script for the wind tunnel data. This script
assumes that the data is stored on the google cloud bucket
'https://storage.googleapis.com/wind_tunnel/' where several datasets
can be stored in zip format. For example:

https://storage.googleapis.com/wind_tunnel/
├── v0.1.tar.gz
├── v0.2.tar.gz
└── v0.3.tar.gz

Each zip file should have the structure:

v0.1.tar.gz
├── 102042348.json
├── 102042349.json
└── 102042350.json

Where each json file corresponds to a different simulation. The json
file should have the following structure:

{
    "nodes": list with shape (N, 3) and dtype float32,
    "edges": list with shape (M, 2) and dtype int32,
    "wind_vector": list with shape (3,) and dtype float32,
    "wind_pressures": list with shape (N,) and dtype float32
}

from datasets import load_dataset
dataset = load_dataset('wind_tunnel', 'v0.1')

'''
import json

import datasets

_DESCRIPTION = 'Wind tunnel dataset example.'

_BASE_URL = 'https://storage.googleapis.com/wind_tunnel/'

_DEFAULT_FLOW_VELOCITY = [0, 0, 0]


class WindTunnel(datasets.GeneratorBasedBuilder):
    '''Wind tunnel builder'''

    def __init__(self, version, **kwargs):
        '''BuilderConfig for WindTunnel.

        Args:
            version: `string`, version of the dataset to use.
        '''
        super().__init__(**kwargs)
        self.version = version
        self.bucket_url = _BASE_URL + f'{version}.tar.gz'

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features({
                'nodes': datasets.Array2D((None, 3), dtype='float32'),
                'edges': datasets.Array2D((None, 2), dtype='int32'),
                'wind_vector': [datasets.Value('float32')],
                'wind_pressures': [datasets.Value('float32')]
            }))

    def _split_generators(self, dl_manager):
        # Download and extract the zip file in the bucket.
        downloaded_dir = dl_manager.download(self.bucket_url)

        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    'sim_dir_paths': dl_manager.iter_archive(downloaded_dir)
                })
        ]

    # pylint: disable=arguments-differ
    def _generate_examples(self, sim_dir_paths):
        for id_, (_, sim_obj) in enumerate(sim_dir_paths):
            bytes_data = sim_obj.read()
            json_data = json.loads(bytes_data)
            nodes = json_data['nodes']
            edges = json_data['edges']
            wind_pressures = json_data['wind_pressures']
            wind_vector = json_data['wind_vector']
            yield id_, {
                'nodes': nodes,
                'edges': edges,
                'wind_vector': wind_vector,
                'wind_pressures': wind_pressures
            }
