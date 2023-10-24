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


def remove_folders_without_file(folders, file_name):
    """Removes folders that do not contain a file"""
    for folder in folders.copy():
        if not os.path.exists(os.path.join(folder, file_name)):
            warnings.warn(f'{folder} does not contain a {file_name} file.')
            folders.remove(folder)


def clean_and_interpolate_mesh(mesh_with_values_path, target_mesh_path,
                               tolerance):
    """Interpolates the mesh with values onto the target mesh."""
    mesh_with_values = pv.read(mesh_with_values_path)
    target_mesh = pv.read(target_mesh_path)
    clean_target_mesh = target_mesh.clean()
    interpolated_mesh = clean_target_mesh.sample(mesh_with_values,
                                                 tolerance=tolerance)
    return interpolated_mesh


def load_flow_velocity(flow_velocity_path):
    """Loads the flow velocity from a json file to a numpy array."""
    with open(flow_velocity_path, encoding='utf-8') as f:
        flow_velocity = json.load(f)
    flow_velocity = np.array(flow_velocity)
    return flow_velocity


def process_folder(folder, openfoam_pressure_field_name, original_mesh_name,
                   wind_vector_name, tolerance, output_dir, nodes_name,
                   edges_name, save_wind_vector_name, wind_pressures_name):
    """Processes a single folder."""
    openfoam_mesh_path = os.path.join(folder, openfoam_pressure_field_name)
    original_mesh_path = os.path.join(folder, original_mesh_name)
    interpolated_mesh = clean_and_interpolate_mesh(openfoam_mesh_path,
                                                   original_mesh_path,
                                                   tolerance)

    # Extract the nodes, edges and pressures from the interpolated mesh.
    nodes, edge_list, pressures = read_nodes_edges_pressures(interpolated_mesh)

    # Load the flow velocity
    wind_vector_path = os.path.join(folder, wind_vector_name)
    if os.path.exists(wind_vector_path):
        wind_vector = load_flow_velocity(wind_vector_path)

    # Save the data.
    save_dir = os.path.join(output_dir, os.path.basename(folder))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    np.save(os.path.join(save_dir, nodes_name), nodes)
    np.save(os.path.join(save_dir, edges_name), edge_list)
    np.save(os.path.join(save_dir, wind_pressures_name), pressures)

    if os.path.exists(wind_vector_path):
        np.save(os.path.join(save_dir, save_wind_vector_name), wind_vector)


def main(_):
    sim_folders = [
        os.path.join(FLAGS.data_dir, f) for f in os.listdir(FLAGS.data_dir)
    ]

    # Remove folders that do not contain a .vtk file.
    remove_folders_without_file(sim_folders,
                                file_name=FLAGS.openfoam_pressure_field_name)
    remove_folders_without_file(sim_folders, file_name=FLAGS.original_mesh_name)

    if not os.path.exists(FLAGS.output_dir):
        os.makedirs(FLAGS.output_dir)

    for folder in sim_folders:
        process_folder(folder, FLAGS.openfoam_pressure_field_name,
                       FLAGS.original_mesh_name, FLAGS.wind_vector_name,
                       FLAGS.tolerance, FLAGS.output_dir, FLAGS.nodes_name,
                       FLAGS.edges_name, FLAGS.save_wind_vector_name,
                       FLAGS.wind_pressures_name)


if __name__ == '__main__':
    app.run(main)
