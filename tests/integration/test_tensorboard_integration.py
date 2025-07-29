import pytest
from txtrboard.client import TensorBoardClient


@pytest.mark.asyncio
async def test_get_runs_from_server(tensorboard_server):
    """Test fetching runs from live TensorBoard server."""
    server_url = tensorboard_server("tacotron2-melvyn-bragg")

    async with TensorBoardClient(server_url) as client:
        runs = await client.get_runs()

        assert len(runs.runs) > 0
        assert isinstance(runs.runs, list)
        # The test data has run named '.'
        assert "." in runs.runs


@pytest.mark.asyncio
async def test_get_environment_from_server(tensorboard_server):
    """Test fetching environment info from live TensorBoard server."""
    server_url = tensorboard_server("tacotron2-melvyn-bragg")

    async with TensorBoardClient(server_url) as client:
        env = await client.get_environment()

        assert hasattr(env, "version")
        assert hasattr(env, "data_location")
        assert isinstance(env.version, str)
        assert len(env.version) > 0


@pytest.mark.asyncio
async def test_get_scalar_data_from_server(tensorboard_server):
    """Test fetching scalar data from live TensorBoard server."""
    server_url = tensorboard_server("tacotron2-melvyn-bragg")

    async with TensorBoardClient(server_url) as client:
        # First get available runs
        runs = await client.get_runs()
        assert len(runs.runs) > 0

        # Get the first run
        run_name = runs.runs[0]

        # Get scalar tags for this run
        tags = await client.get_scalar_tags(run_name)
        assert run_name in tags.root

        # Should have some scalar tags
        run_tags = tags.root[run_name]
        assert len(run_tags) > 0

        # Get data for the first tag
        tag_name = list(run_tags.keys())[0]
        data = await client.get_scalar_data(run_name, tag_name)

        # Should have data points
        assert len(data.root) > 0

        # Each data point should be [wall_time, step, value]
        first_point = data.root[0]
        assert len(first_point) == 3
        assert isinstance(first_point[0], (int, float))  # wall_time
        assert isinstance(first_point[1], (int, float))  # step
        assert isinstance(first_point[2], (int, float))  # value

        # Test conversion to ScalarDatum objects
        scalar_data = data.as_scalar_data()
        assert len(scalar_data) == len(data.root)

        first_datum = scalar_data[0]
        assert hasattr(first_datum, "wall_time")
        assert hasattr(first_datum, "step")
        assert hasattr(first_datum, "value")


@pytest.mark.asyncio
async def test_multiple_runs_and_tags(tensorboard_server):
    """Test handling multiple runs and their scalar tags."""
    server_url = tensorboard_server("tacotron2-melvyn-bragg")

    async with TensorBoardClient(server_url) as client:
        runs = await client.get_runs()

        # Test each run
        for run_name in runs.runs:
            tags = await client.get_scalar_tags(run_name)

            if run_name in tags.root and tags.root[run_name]:
                # Get data for first available tag
                tag_name = list(tags.root[run_name].keys())[0]
                data = await client.get_scalar_data(run_name, tag_name)

                # Verify data structure
                assert len(data.root) >= 0  # May be empty for some tags

                if len(data.root) > 0:
                    # Verify each point has correct structure
                    for point in data.root:
                        assert len(point) == 3
                        assert all(isinstance(x, (int, float)) for x in point)
