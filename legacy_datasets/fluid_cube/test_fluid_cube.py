"""Tests the fluid cube dataset"""
import datasets


def test_shapes_of_examples():
    """If the shape of every simulation step is the same through the example."""
    dataset = datasets.load_dataset('./legacy_datasets/fluid_cube/fluid_cube',
                                    version='10_simulations',
                                    split='train',
                                    streaming=True,
                                    trust_remote_code=True)
    for example in dataset:
        simulation_time_steps = example['simulation_time_steps']
        first_time_step = simulation_time_steps[0]
        for time_step in range(1, len(simulation_time_steps)):
            assert len(first_time_step) == len(simulation_time_steps[time_step])
