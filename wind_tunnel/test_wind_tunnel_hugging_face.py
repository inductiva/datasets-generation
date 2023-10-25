"""Tests for the wind tunnel hugging face datasets."""
import datasets


def test_shapes_of_examples():
    """Test number of nodes == number of wind pressures measurements."""
    dataset = datasets.load_dataset('wind_tunnel/wind_tunnel/',
                                    version='5_sims_flow_20_40_processed',
                                    split='train')
    for example in dataset:
        nodes = example['nodes']
        wind_pressures = example['wind_pressures']

        assert len(nodes) == len(wind_pressures)
