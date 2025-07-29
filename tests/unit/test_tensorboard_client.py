import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from txtrboard.client import (
    TensorBoardClient,
    TensorBoardConnectionError,
    TensorBoardAPIError,
)


class TestTensorBoardClient:
    """Test suite for TensorBoard HTTP client."""

    def test_client_initialization(self):
        """Test client initializes with correct defaults."""
        client = TensorBoardClient()
        assert client.base_url == "http://localhost:6006"
        assert client.timeout == 10.0
        assert isinstance(client.client, httpx.AsyncClient)

        # Test custom initialization
        client = TensorBoardClient("http://example.com:8080", timeout=5.0)
        assert client.base_url == "http://example.com:8080"
        assert client.timeout == 5.0

    def test_base_url_normalization(self):
        """Test that trailing slashes are removed from base URL."""
        client = TensorBoardClient("http://localhost:6006/")
        assert client.base_url == "http://localhost:6006"

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TensorBoardClient()
        response = await client._make_request("/data/test")

        assert response == mock_response
        mock_get.assert_called_once_with("http://localhost:6006/data/test", params=None)

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_make_request_with_params(self, mock_get):
        """Test API request with query parameters."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TensorBoardClient()
        params = {"run": "test_run", "tag": "loss"}
        await client._make_request("/data/test", params=params)

        mock_get.assert_called_once_with("http://localhost:6006/data/test", params=params)

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_get):
        """Test handling of connection errors."""
        mock_get.side_effect = httpx.ConnectError("Connection failed")

        client = TensorBoardClient()
        with pytest.raises(TensorBoardConnectionError) as exc_info:
            await client._make_request("/data/test")

        assert "Unable to connect to TensorBoard" in str(exc_info.value)

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, mock_get):
        """Test handling of timeout errors."""
        mock_get.side_effect = httpx.TimeoutException("Request timeout")

        client = TensorBoardClient()
        with pytest.raises(TensorBoardConnectionError) as exc_info:
            await client._make_request("/data/test")

        assert "Request timeout" in str(exc_info.value)

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_http_error_handling(self, mock_get):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("404 Not Found", request=Mock(), response=Mock())
        mock_get.return_value = mock_response

        client = TensorBoardClient()
        with pytest.raises(TensorBoardAPIError) as exc_info:
            await client._make_request("/data/test")

        assert "TensorBoard API error" in str(exc_info.value)

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_get_environment(self, mock_get):
        """Test getting environment information."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "version": "2.8.0",
            "data_location": "/tmp/logs",
            "window_title": "Test",
            "experiment_name": "",
            "experiment_description": "",
            "creation_time": 1234567890.0,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TensorBoardClient()
        env = await client.get_environment()

        assert env.version == "2.8.0"
        assert env.data_location == "/tmp/logs"
        mock_get.assert_called_once_with("http://localhost:6006/data/environment", params=None)

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_get_logdir(self, mock_get):
        """Test getting log directory."""
        mock_response = Mock()
        mock_response.json.return_value = {"logdir": "/tmp/tensorboard_logs"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TensorBoardClient()
        logdir = await client.get_logdir()

        assert logdir.logdir == "/tmp/tensorboard_logs"
        mock_get.assert_called_once_with("http://localhost:6006/data/logdir", params=None)

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_get_runs(self, mock_get):
        """Test getting runs list."""
        mock_response = Mock()
        mock_response.json.return_value = ["train", "eval", "test"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TensorBoardClient()
        runs = await client.get_runs()

        assert runs.runs == ["train", "eval", "test"]
        mock_get.assert_called_once_with("http://localhost:6006/data/runs", params=None)

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_get_scalar_tags(self, mock_get):
        """Test getting scalar tags for a run."""
        mock_response = Mock()
        mock_response.json.return_value = {"train": {"loss": {"displayName": "Loss", "description": "Training loss"}}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TensorBoardClient()
        tags = await client.get_scalar_tags("train")

        assert "train" in tags.root
        assert "loss" in tags.root["train"]
        assert tags.root["train"]["loss"].displayName == "Loss"
        mock_get.assert_called_once_with(
            "http://localhost:6006/data/plugin/scalars/tags", params={"run": "train"}
        )

    @patch("txtrboard.client.httpx.AsyncClient.get")
    @pytest.mark.asyncio
    async def test_get_scalar_data(self, mock_get):
        """Test getting scalar data for a run and tag."""
        mock_response = Mock()
        mock_response.json.return_value = [[1234567890.0, 0, 0.5], [1234567900.0, 10, 0.3]]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client = TensorBoardClient()
        data = await client.get_scalar_data("train", "loss")

        assert len(data.root) == 2
        assert data.root[0] == [1234567890.0, 0, 0.5]
        assert data.root[1] == [1234567900.0, 10, 0.3]

        # Test conversion to ScalarDatum objects
        scalar_data = data.as_scalar_data()
        assert len(scalar_data) == 2
        assert scalar_data[0].step == 0
        assert scalar_data[0].value == 0.5
        assert scalar_data[1].step == 10
        assert scalar_data[1].value == 0.3

        mock_get.assert_called_once_with(
            "http://localhost:6006/data/plugin/scalars/scalars",
            params={"run": "train", "tag": "loss", "format": "JSON"}
        )

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client works as async context manager."""
        with patch.object(TensorBoardClient, "close") as mock_close:
            mock_close.return_value = AsyncMock()
            async with TensorBoardClient() as client:
                assert isinstance(client, TensorBoardClient)
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_method(self):
        """Test client close method."""
        client = TensorBoardClient()
        with patch.object(client.client, "aclose") as mock_close:
            mock_close.return_value = AsyncMock()
            await client.close()
            mock_close.assert_called_once()
