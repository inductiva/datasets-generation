# Overview

This repository contains two scripts to facilitate the generation and post-processing of 3D meshes. The meshes are generated from a dataset of images and further processed to ensure they are clean and aligned to their principal axes. These scripts use InstantMesh model for mesh generation and PyVista for mesh manipulation.



# Scripts

## generate_meshes.py

This script generates 3D meshes from a dataset of images and allows optional post-processing of the generated meshes. The meshes are generated using a template command for Instant Meshes and saved in the specified directories.

### Flags

-	--input_path: Path to the input dataset (default: data/cars196)
-	--config_file: Path to the InstantMesh configuration file (default: configs/instant-mesh-large.yaml)
-	--output_path: Path to the output directory (default: data/output)
-	--output_subdir: Subdirectory for output (default: instant-mesh-large)
-	--postprocess_meshes: Whether to post-process the meshes after generation (default: True)
-	--debug: Enable debug logging (default: False)


### Usage

```bash
python generate_meshes.py \
    --input_path="path/to/images" \
    --config_file="path/to/config.yaml" \
    --output_path="path/to/output" \
    --output_subdir="instant-mesh-large" \
    --postprocess_meshes=True \
    --debug
```

### Key Functionality

- 	**Mesh Generation**: The script iterates over image files and uses a template command to generate meshes with InstantMesh. The generated mesh files are renamed and saved in the output directory.
-	**Post-processing**: If enabled, the generated meshes are post-processed using the functions from postprocess_mesh.py.



## postprocess_mesh.py

This script provides functions to clean and align the generated 3D meshes. It ensures that only the largest connected region of the mesh is kept and that the mesh is aligned to its principal axes.

### Key Functions

-   `_extract_largest_connected_region(mesh)`: Identifies and extracts the largest connected region from the mesh.
-   `_align_mesh_to_principal_axes(mesh)`: Aligns the mesh to its principal axes based on an eigen decomposition of the mesh’s covariance matrix.
-   `postprocess_mesh(obj_path, save_path)`: Combines the cleaning and alignment functions to post-process a mesh and save it in .obj format.

### Example Usage

This script is used by generate_meshes.py for post-processing but can also be run independently by importing the functions and calling them directly

```python
from postprocess_mesh import postprocess_mesh

postprocess_mesh("path/to/mesh.obj", "path/to/processed_mesh.obj")
```