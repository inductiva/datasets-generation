"""Pre-processes the raw simulation data into numpy arrays

Assumes the data is in the following format:

    - data
        - id_1
            - pressure_field.vtk
            - object.obj
            - flow_velocity.json
        - id_2
            - pressure_field.vtk
            - object.obj
            - flow_velocity.json

It processes the data and stores it in the following format:

    - data
        - id_1
            - nodes.npy
            - edges.npy
            - flow_velocity.npy
            - wind_pressures.npy 
        - id_2
            - nodes.npy
            - edges.npy
            - flow_velocity.npy
            - wind_pressures.npy

NOTE: Here we assume undirected edges, hence each pair (i, j) appears
only once in the adjancecy list. Several ML frameworks, such as
pytorch, always represent graphs as directed. Hence, to use pytorch we
need to duplicate each edge (i, j) as (j, i) in the adjacency list.

"""
import os
import json
import warnings

from absl import app
from absl import flags

import pyvista as pv
import numpy as np

FLAGS = flags.FLAGS

flags.DEFINE_string('data_dir', None,
                    'Path to the folder containing the mesh files.')

flags.DEFINE_string('openfoam_pressure_field_name', 'pressure_field.vtk',
                    'Name of the original pressure field.')
flags.DEFINE_string('original_mesh_name', 'object.obj',
                    'Name of the original mesh.')
flags.DEFINE_string('wind_vector_name', 'flow_velocity.json',
                    'The name of the file containing the wind vector.')

flags.DEFINE_string(
    'output_dir', None,
    'Path to the folder where the processed data will be saved.')

flags.DEFINE_string('nodes_name', 'nodes.npy',
                    'Name of the file containing the nodes.')
flags.DEFINE_string('edges_name', 'edges.npy',
                    'Name of the file containing the edges.')
flags.DEFINE_string('save_wind_vector_name', 'flow_velocity.npy',
                    'Name of the file containing the flow velocity.')
flags.DEFINE_string('wind_pressures_name', 'wind_pressures.npy',
                    'Name of the file containing the wind pressures.')

flags.DEFINE_float('tolerance', 1.5, 'Tolerance for the mesh sampling.')

flags.mark_flag_as_required('data_dir')
flags.mark_flag_as_required('output_dir')


def read_nodes_edges_pressures(mesh):
    edge_mesh = mesh.extract_all_edges(use_all_points=True)
    edge_list = edge_mesh.lines.reshape(-1, 3)[:, 1:]
    nodes = mesh.points
    pressures = mesh.get_array('p', preference='point')
    return nodes, edge_list, pressures


def main(_):
    sim_folders = [
        os.path.join(FLAGS.data_dir, f) for f in os.listdir(FLAGS.data_dir)
    ]

    # Remove folders that do not contain a .vtk file.
    for folder in sim_folders.copy():
        if not os.path.exists(
                os.path.join(folder, FLAGS.openfoam_pressure_field_name)):
            warnings.warn(f'{folder} does not contain a .vtk file.')
            sim_folders.remove(folder)

    if not os.path.exists(FLAGS.output_dir):
        os.makedirs(FLAGS.output_dir)

    for folder in sim_folders:
        openfoam_mesh_path = os.path.join(folder,
                                          FLAGS.openfoam_pressure_field_name)
        original_mesh_path = os.path.join(folder, FLAGS.original_mesh_name)

        openfoam_mesh = pv.read(openfoam_mesh_path)
        original_mesh = pv.read(original_mesh_path)
        original_mesh = original_mesh.clean()

        # Map the mesh created by open foam to the original mesh of
        # the submited object.
        interpolated_mesh = original_mesh.sample(openfoam_mesh,
                                                 tolerance=FLAGS.tolerance)

        # Extract the nodes, edges and pressures from the interpolated mesh.
        nodes, edge_list, pressures = read_nodes_edges_pressures(
            interpolated_mesh)

        # Load the flow velocity
        wind_vector_path = os.path.join(folder, FLAGS.wind_vector_name)
        if os.path.exists(wind_vector_path):
            with open(wind_vector_path, encoding='utf-8') as f:
                wind_vector = json.load(f)
            wind_vector = np.array(wind_vector)

        # Save the data.
        save_dir = os.path.join(FLAGS.output_dir, os.path.basename(folder))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        np.save(os.path.join(save_dir, FLAGS.nodes_name), nodes)
        np.save(os.path.join(save_dir, FLAGS.edges_name), edge_list)
        np.save(os.path.join(save_dir, FLAGS.wind_pressures_name), pressures)

        if os.path.exists(wind_vector_path):
            np.save(os.path.join(save_dir, FLAGS.save_wind_vector_name),
                    wind_vector)


if __name__ == '__main__':
    app.run(main)
