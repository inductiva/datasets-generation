# Wind Tunnel Dataset Generation

This project generates datasets using the `wind-tunnel` library for simulations.

## Installation

To install `datasets-generation` and its dependencies, follow these steps:

1. Clone the repository:

   ```bash
   $ git clone https://github.com/inductiva/datasets-generation.git
   $ cd datasets-generation
   ```
   
2. Install the project dependencies:
   ```bash
   $ pip install -r requirements.txt
   ```

3. Install `InstantMesh` for mesh generation (optional):
   
    Follow the instructions at https://github.com/TencentARC/InstantMesh.

## Usage

1. **Mesh Generation**: We provide a script for mesh generation using `InstantMesh`.
   ```bash
   $ python src/scripts/generate_meshes.py
   ```

2. **Dataset Generation**: Run the main script to generate the dataset.
   ```bash
   $ python src/run.py
   ```

3. **HuggingFace Dataset**: WIP
