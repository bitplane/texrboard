import pytest
import tarfile
from pathlib import Path


@pytest.fixture
def logdir(tmpdir_factory):
    """Fixture that provides access to extracted TensorBoard log directories.

    Usage:
        def test_something(logdir):
            path = logdir('tacotron2-melvyn-bragg')
            # do stuff with the path

    The fixture extracts ./tests/data/{name}.tar.gz into a temporary directory
    and returns the path. Cleanup is handled automatically by pytest.
    """

    def _load_logdir(name: str) -> str:
        # Path to the archive file
        archive_path = Path(__file__).parent / "data" / f"{name}.tar.gz"

        if not archive_path.exists():
            available_files = []
            data_dir = Path(__file__).parent / "data"
            if data_dir.exists():
                available_files = [f.stem.replace(".tar", "") for f in data_dir.glob("*.tar.gz")]

            raise FileNotFoundError(
                f"Archive {name}.tar.gz not found in tests/data/. " f"Available archives: {available_files}"
            )

        # Create temporary directory
        tmpdir = tmpdir_factory.mktemp(f"logdir_{name}")

        # Extract archive with filter for Python 3.14 compatibility
        with tarfile.open(archive_path, "r:gz") as tar:
            # Use 'data' filter to safely extract (available in Python 3.12+)
            try:
                tar.extractall(path=tmpdir, filter="data")
            except TypeError:
                # Fallback for older Python versions
                tar.extractall(path=tmpdir)

        # If there's only one directory in the extraction, return that directory
        contents = list(tmpdir.listdir())
        if len(contents) == 1 and contents[0].isdir():
            return str(contents[0])

        return str(tmpdir)

    return _load_logdir
