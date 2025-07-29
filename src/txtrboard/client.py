import httpx
from typing import Optional, Dict
from urllib.parse import urljoin
from txtrboard.models.tensorboard import (
    EnvironmentResponse,
    LogdirResponse,
    RunsResponse,
    PluginsListingResponse,
    ScalarTagsResponse,
    ScalarDataResponse,
    ImageTagsResponse,
    ImageDataResponse,
    AudioTagsResponse,
    AudioDataResponse,
    DistributionTagsResponse,
    DistributionDataResponse,
    TextTagsResponse,
    TextDataResponse,
)
from txtrboard.logging_config import get_logger


class TensorBoardClientError(Exception):
    """Base exception for TensorBoard client errors."""

    pass


class TensorBoardConnectionError(TensorBoardClientError):
    """Raised when unable to connect to TensorBoard server."""

    pass


class TensorBoardAPIError(TensorBoardClientError):
    """Raised when TensorBoard API returns an error."""

    pass


class TensorBoardClient:
    """HTTP client for TensorBoard's web API.

    Provides methods to fetch data from a running TensorBoard server
    using the official HTTP API endpoints.
    """

    def __init__(self, base_url: str = "http://localhost:6006", timeout: float = 10.0):
        """Initialize TensorBoard client.

        Args:
            base_url: Base URL of TensorBoard server (default: http://localhost:6006)
            timeout: Request timeout in seconds
        """
        self.logger = get_logger(__name__)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self.logger.info(f"TensorBoardClient initialized with URL: {self.base_url}")

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> httpx.Response:
        """Make HTTP request to TensorBoard API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Response object

        Raises:
            TensorBoardConnectionError: If unable to connect
            TensorBoardAPIError: If API returns error status
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response
        except httpx.ConnectError as e:
            raise TensorBoardConnectionError(f"Unable to connect to TensorBoard at {self.base_url}: {e}")
        except httpx.TimeoutException as e:
            raise TensorBoardConnectionError(f"Request timeout connecting to TensorBoard: {e}")
        except httpx.HTTPStatusError as e:
            raise TensorBoardAPIError(f"TensorBoard API error: {e}")

    async def get_environment(self) -> EnvironmentResponse:
        """Get TensorBoard environment information.

        Returns:
            Environment response with version and data location
        """
        response = await self._make_request("/data/environment")
        return EnvironmentResponse(**response.json())

    async def get_logdir(self) -> LogdirResponse:
        """Get the log directory being served by TensorBoard.

        Returns:
            Logdir response with directory path
        """
        response = await self._make_request("/data/logdir")
        return LogdirResponse(**response.json())

    async def get_runs(self) -> RunsResponse:
        """Get list of all runs known to TensorBoard.

        Returns:
            Runs response with list of run names
        """
        self.logger.debug("get_runs() called")
        response = await self._make_request("/data/runs")
        self.logger.debug(f"get_runs() got response: {type(response)}")

        json_data = response.json()
        self.logger.debug(f"get_runs() response.json(): {type(json_data)}, value: {json_data}")

        runs_response = RunsResponse(runs=json_data)
        self.logger.debug(f"get_runs() returning RunsResponse: {type(runs_response)}, runs: {runs_response.runs}")
        return runs_response

    async def get_plugins_listing(self) -> PluginsListingResponse:
        """Get available plugins and their paths.

        Returns:
            Plugins listing response
        """
        response = await self._make_request("/data/plugins_listing")
        return PluginsListingResponse(response.json())

    async def get_scalar_tags(self, run: str) -> ScalarTagsResponse:
        """Get scalar tags for a specific run.

        Args:
            run: Run name

        Returns:
            Scalar tags response with tag information
        """
        response = await self._make_request("/data/plugin/scalars/tags", params={"run": run})
        return ScalarTagsResponse(response.json())

    async def get_scalar_data(self, run: str, tag: str, format: str = "JSON") -> ScalarDataResponse:
        """Get scalar data for a specific run and tag.

        Args:
            run: Run name
            tag: Tag name
            format: Data format (default: JSON)

        Returns:
            Scalar data response with time series data
        """
        params = {"run": run, "tag": tag, "format": format}
        response = await self._make_request("/data/plugin/scalars/scalars", params=params)
        return ScalarDataResponse(response.json())

    async def get_image_tags(self) -> ImageTagsResponse:
        """Get image tags for all runs.

        Returns:
            Image tags response
        """
        response = await self._make_request("/data/plugin/images/tags")
        return ImageTagsResponse(response.json())

    async def get_image_data(self, run: str, tag: str, sample: int = 0) -> ImageDataResponse:
        """Get image metadata for a specific run and tag.

        Args:
            run: Run name
            tag: Tag name
            sample: Sample index (default: 0)

        Returns:
            Image data response with metadata
        """
        params = {"run": run, "tag": tag, "sample": sample}
        response = await self._make_request("/data/plugin/images/images", params=params)
        return ImageDataResponse(response.json())

    async def get_audio_tags(self) -> AudioTagsResponse:
        """Get audio tags for all runs.

        Returns:
            Audio tags response
        """
        response = await self._make_request("/data/plugin/audio/tags")
        return AudioTagsResponse(response.json())

    async def get_audio_data(self, run: str, tag: str, sample: int = 0) -> AudioDataResponse:
        """Get audio metadata for a specific run and tag.

        Args:
            run: Run name
            tag: Tag name
            sample: Sample index (default: 0)

        Returns:
            Audio data response with metadata
        """
        params = {"run": run, "tag": tag, "sample": sample}
        response = await self._make_request("/data/plugin/audio/audio", params=params)
        return AudioDataResponse(response.json())

    async def get_distribution_tags(self) -> DistributionTagsResponse:
        """Get distribution/histogram tags for all runs.

        Returns:
            Distribution tags response
        """
        response = await self._make_request("/data/plugin/distributions/tags")
        return DistributionTagsResponse(response.json())

    async def get_distribution_data(self, run: str, tag: str) -> DistributionDataResponse:
        """Get distribution data for a specific run and tag.

        Args:
            run: Run name
            tag: Tag name

        Returns:
            Distribution data response with histogram data
        """
        params = {"run": run, "tag": tag}
        response = await self._make_request("/data/plugin/distributions/distributions", params=params)
        return DistributionDataResponse(response.json())

    async def get_text_tags(self) -> TextTagsResponse:
        """Get text tags for all runs.

        Returns:
            Text tags response
        """
        response = await self._make_request("/data/plugin/text/tags")
        return TextTagsResponse(response.json())

    async def get_text_data(self, run: str, tag: str) -> TextDataResponse:
        """Get text data for a specific run and tag.

        Args:
            run: Run name
            tag: Tag name

        Returns:
            Text data response
        """
        params = {"run": run, "tag": tag}
        response = await self._make_request("/data/plugin/text/text", params=params)
        return TextDataResponse(response.json())

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
