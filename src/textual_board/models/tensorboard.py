from pydantic import BaseModel, RootModel
from typing import Dict, List, Optional, Union


# --- /data/environment ---
class EnvironmentResponse(BaseModel):
    version: str
    data_location: str
    window_title: str
    experiment_name: str
    experiment_description: str
    creation_time: float


# --- /data/logdir ---
class LogdirResponse(BaseModel):
    logdir: str


# --- /data/runs ---
class RunsResponse(BaseModel):
    runs: List[str]


# --- /data/plugins_listing ---
class PluginsListingResponse(RootModel[Dict[str, str]]):
    """Plugin name -> path mapping."""

    pass


# --- /data/plugin/SCALAR/tags ---
class ScalarTagInfo(BaseModel):
    displayName: str
    description: str


class ScalarTagsResponse(RootModel[Dict[str, Dict[str, ScalarTagInfo]]]):
    """Run -> tag -> info mapping."""

    pass


# --- /data/plugin/SCALAR/data ---
class ScalarDatum(BaseModel):
    wall_time: float
    step: int
    value: float

    @classmethod
    def from_array(cls, data: List[Union[float, int]]) -> "ScalarDatum":
        """Create ScalarDatum from [wall_time, step, value] array."""
        return cls(wall_time=data[0], step=data[1], value=data[2])


class ScalarDataResponse(RootModel[List[List[Union[float, int]]]]):
    """List of scalar data points as [wall_time, step, value] arrays."""

    def as_scalar_data(self) -> List[ScalarDatum]:
        """Convert to list of ScalarDatum objects."""
        return [ScalarDatum.from_array(point) for point in self.root]


# --- /data/plugin/images/tags ---
class ImageTagMeta(BaseModel):
    displayName: str
    description: str
    samples: int


class ImageTagsResponse(RootModel[Dict[str, Dict[str, ImageTagMeta]]]):
    """Run -> tag -> meta mapping."""

    pass


# --- /data/plugin/images/images ---
class ImageMetadata(BaseModel):
    wall_time: float
    step: int
    width: int
    height: int
    query: str


class ImageDataResponse(RootModel[List[ImageMetadata]]):
    """List of image metadata."""

    pass


# --- /data/plugin/audio/tags ---
class AudioTagMeta(BaseModel):
    displayName: str
    description: str
    samples: int


class AudioTagsResponse(RootModel[Dict[str, Dict[str, AudioTagMeta]]]):
    """Run -> tag -> meta mapping."""

    pass


# --- /data/plugin/audio/audio ---
class AudioMetadata(BaseModel):
    wall_time: float
    step: int
    content_type: str  # usually "audio/wav"
    query: str


class AudioDataResponse(RootModel[List[AudioMetadata]]):
    """List of audio metadata."""

    pass


# --- /data/plugin/distribution/tags ---
class DistributionTagsResponse(RootModel[Dict[str, Dict[str, Dict]]]):
    """Run -> tag -> {} mapping."""

    pass


# --- /data/plugin/distribution/distributions ---
class DistributionDatum(BaseModel):
    wall_time: float
    step: int
    buckets: List[float]
    bucket_limits: List[float]


class DistributionDataResponse(RootModel[List[DistributionDatum]]):
    """List of distribution data."""

    pass


# --- /data/plugin/graph/run_metadata ---
class RunMetadata(BaseModel):
    tag: str
    run: str


class RunMetadataResponse(RootModel[List[RunMetadata]]):
    """List of run metadata."""

    pass


# --- /data/plugin/graph/graph ---
class GraphDataResponse(BaseModel):
    graph_def: str  # JSON pbtxt format
    version: int


# --- /data/plugin/text/tags ---
class TextTagMeta(BaseModel):
    displayName: str
    description: str
    samples: int


class TextTagsResponse(RootModel[Dict[str, Dict[str, TextTagMeta]]]):
    """Run -> tag -> meta mapping."""

    pass


# --- /data/plugin/text/text ---
class TextDatum(BaseModel):
    wall_time: float
    step: int
    text: str


class TextDataResponse(RootModel[List[TextDatum]]):
    """List of text data."""

    pass


# --- Generic fallback for unknown/custom plugins ---
class GenericPluginResponse(RootModel[Dict[str, Optional[Dict]]]):
    """Generic plugin response."""

    pass
