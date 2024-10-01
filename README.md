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
   $ python windtunnel_dataset/scripts/generate_meshes.py
   ```


2. **Generate submission parameters**: You can change the script to customize the simulations parameters:
   ```bash
   $ python windtunnel_dataset/save_params.py
   ```
   
3. **Submit simulations**: Run this script to submit the simulations with the previously generated parameters:
   ```bash
   $ python windtunnel_dataset/run_simulations.py
   ```

4. **Download and postprocess the simulations**: Finally download the simulations and do some postprocessing:
   ```bash
   $ python windtunnel_dataset/download_simulations.py
   ```
