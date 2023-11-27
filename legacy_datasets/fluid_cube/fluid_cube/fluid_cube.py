"""Dataset for the fluid cube

More on: https://inductiva.ai/blog/article/fluid-cube-dataset

"""
import json

import datasets
import numpy as np

_DESCRIPTION = 'https://inductiva.ai/blog/article/fluid-cube-dataset'

_BASE_URL = 'https://storage.googleapis.com/fluid_cube/'


class WindTunnel(datasets.GeneratorBasedBuilder):
    '''The FluidCube builder'''

    def __init__(self, version, **kwargs):
        super().__init__(**kwargs)
        self.bucket_url = _BASE_URL + f'{version}.tar.gz'

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features({
                'block_position': [datasets.Value('float32')],
                'block_dimensions': [datasets.Value('float32')],
                'fluid_volume':
                    datasets.Value('float32'),
                'block_velocity': [datasets.Value('float32')],
                'block_velocity_magnitude':
                    datasets.Value('float32'),
                'kinematic_viscosity':
                    datasets.Value('float32'),
                'density':
                    datasets.Value('float32'),
                'tank_dimensions': [datasets.Value('float32')],
                'time_max':
                    datasets.Value('float32'),
                'time_step':
                    datasets.Value('float32'),
                'particle_radius':
                    datasets.Value('float32'),
                'number_of_fluid_particles':
                    datasets.Value('int32'),
                # Float64 because pyArrow is not capable of
                # [Array2D(shape, float32)].
                # https://github.com/huggingface/datasets/issues/5936
                'simulation_time_steps':
                    datasets.Sequence(
                        datasets.Array2D(dtype='float64', shape=(None, 6)))
            }))

    def _split_generators(self, dl_manager):
        # Download and extract the zip file in the bucket.
        downloaded_dir = dl_manager.download(self.bucket_url)
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={
                    'json_files': dl_manager.iter_archive(downloaded_dir)
                })
        ]

    # pylint: disable=arguments-differ
    def _generate_examples(self, json_files):
        for id_, (_, json_file) in enumerate(json_files):
            bytes_data = json_file.read()
            data = json.loads(bytes_data)
            data['simulation_time_steps'] = [
                np.transpose(a) for a in data['simulation_time_steps']
            ]
            yield id_, data
