import os
from pathlib import Path


def test_logdir_fixture_extracts_test_archive(logdir):
    """Test that logdir fixture can extract test.tar.gz and access README.md."""
    path = logdir("test")

    # Path should exist and be a directory
    assert os.path.exists(path)
    assert os.path.isdir(path)

    # Should contain README.md from the test archive
    readme_path = Path(path) / "README.md"
    assert readme_path.exists()

    # Should be able to read the content
    content = readme_path.read_text()
    assert len(content.strip()) > 0


def test_logdir_fixture_missing_archive_fails(logdir):
    """Test that logdir fixture fails appropriately for missing archives."""
    try:
        logdir("nonexistent-archive")
        assert False, "Should have raised an error for missing archive"
    except FileNotFoundError:
        pass  # Expected behavior
