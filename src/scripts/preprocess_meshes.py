import pyvista as pv
import vtk
import trimesh
from vtk.util import numpy_support
import numpy as np


def _extract_largest_connected_region(mesh):
    """
    Extract and return the largest connected region from the given mesh.

    This function performs the following steps:
    1. Applies a connectivity filter to identify and color all connected regions in the surface.
    2. Identifies the largest connected region based on the number of cells.
    3. Extracts the largest connected region from the mesh.
    4. Returns the largest connected region as a new mesh object.

    Parameters:
    mesh (pyvista.PolyData): The input mesh to be cleaned.

    Returns:
    pyvista.PolyData: The largest connected region of the input mesh.
    """
    poly_data = mesh.cast_to_unstructured_grid().extract_surface()

    connectivity_filter = vtk.vtkConnectivityFilter()
    connectivity_filter.SetInputData(poly_data)
    connectivity_filter.SetExtractionModeToAllRegions()
    connectivity_filter.ColorRegionsOn()
    connectivity_filter.Update()

    regions = connectivity_filter.GetOutput()

    region_ids = numpy_support.vtk_to_numpy(
        regions.GetCellData().GetArray("RegionId"))

    unique_region_ids, counts = np.unique(region_ids, return_counts=True)

    largest_region_id = unique_region_ids[np.argmax(counts)]

    connectivity_filter.SetExtractionModeToSpecifiedRegions()
    connectivity_filter.InitializeSpecifiedRegionList()
    connectivity_filter.AddSpecifiedRegion(largest_region_id)
    connectivity_filter.Update()

    largest_region = pv.wrap(connectivity_filter.GetOutput())

    return largest_region


def _align_mesh_to_principal_axes(mesh):
    """
    Align the given mesh to its principal axes.

    This function performs the following steps:
    1. Calculates the centroid of the mesh points and centers the points around the centroid.
    2. Computes the covariance matrix of the centered points.
    3. Performs an eigen decomposition of the covariance matrix to find the principal axes.
    4. Constructs a transformation matrix to align the mesh with its principal axes.
    5. Applies the transformation to the mesh and returns the aligned mesh.

    Parameters:
    mesh (pyvista.PolyData): The input mesh to be aligned.

    Returns:
    pyvista.PolyData: The mesh aligned to its principal axes.
    """
    points = mesh.points
    centroid = np.mean(points, axis=0)
    centered_points = points - centroid
    covariance_matrix = np.cov(centered_points, rowvar=False)

    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

    sorted_indices = np.argsort(eigenvalues)[::-1]
    principal_axes = eigenvectors[:, sorted_indices]

    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = principal_axes.T

    aligned_mesh = mesh.copy()
    aligned_mesh.transform(transformation_matrix)

    aligned_mesh = aligned_mesh.rotate_x(-90)

    aligned_mesh.save('temp_mesh.stl')
    aligned_mesh = trimesh.load_mesh('temp_mesh.stl')

    return aligned_mesh


def preprocess_mesh(obj_path, save_path):
    """
    Extracts the largest connected region and aligns the mesh to the principal axes
    """
    mesh = pv.read(obj_path)
            
    mesh = _extract_largest_connected_region(mesh)

    mesh = mesh.rotate_y(180)

    mesh = _align_mesh_to_principal_axes(mesh)

    mesh.export(save_path, file_type='obj')
