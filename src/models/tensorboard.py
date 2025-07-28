from pydantic import BaseModel
from typing import Dict, List, Optional


# --- /data/environment ---
class EnvironmentResponse(BaseModel):
    data_location: str
    tensorboard_version: str


# --- /data/logdir ---
class LogdirResponse(BaseModel):
    logdir: str


# --- /data/runs ---
class RunsResponse(BaseModel):
    runs: List[str]


# --- /data/plugins_listing ---
class PluginsListingResponse(BaseModel):
    __root__: Dict[str, str]  # plugin_name -> path


# --- /data/plugin/SCALAR/tags ---
class ScalarTagInfo(BaseModel):
    displayName: str
    description: str


class ScalarTagsResponse(BaseModel):
    __root__: Dict[str, ScalarTagInfo]  # tag -> info


# --- /data/plugin/SCALAR/data ---
class ScalarDatum(BaseModel):
    wall_time: float
    step: int
    value: float


class ScalarDataResponse(BaseModel):
    __root__: List[ScalarDatum]


# --- /data/plugin/images/tags ---
class ImageTagMeta(BaseModel):
    displayName: str
    description: str
    samples: int


class ImageTagsResponse(BaseModel):
    __root__: Dict[str, Dict[str, ImageTagMeta]]  # run -> tag -> meta


# --- /data/plugin/images/images ---
class ImageMetadata(BaseModel):
    wall_time: float
    step: int
    width: int
    height: int
    query: str


class ImageDataResponse(BaseModel):
    __root__: List[ImageMetadata]


# --- /data/plugin/audio/tags ---
class AudioTagMeta(BaseModel):
    displayName: str
    description: str
    samples: int


class AudioTagsResponse(BaseModel):
    __root__: Dict[str, Dict[str, AudioTagMeta]]  # run -> tag -> meta


# --- /data/plugin/audio/audio ---
class AudioMetadata(BaseModel):
    wall_time: float
    step: int
    content_type: str  # usually "audio/wav"
    query: str


class AudioDataResponse(BaseModel):
    __root__: List[AudioMetadata]


# --- /data/plugin/distribution/tags ---
class DistributionTagsResponse(BaseModel):
    __root__: Dict[str, Dict[str, Dict]]  # run -> tag -> {}


# --- /data/plugin/distribution/distributions ---
class DistributionDatum(BaseModel):
    wall_time: float
    step: int
    buckets: List[float]
    bucket_limits: List[float]


class DistributionDataResponse(BaseModel):
    __root__: List[DistributionDatum]


# --- /data/plugin/graph/run_metadata ---
class RunMetadata(BaseModel):
    tag: str
    run: str


class RunMetadataResponse(BaseModel):
    __root__: List[RunMetadata]


# --- /data/plugin/graph/graph ---
class GraphDataResponse(BaseModel):
    graph_def: str  # JSON pbtxt format
    version: int


# --- /data/plugin/text/tags ---
class TextTagMeta(BaseModel):
    displayName: str
    description: str
    samples: int


class TextTagsResponse(BaseModel):
    __root__: Dict[str, Dict[str, TextTagMeta]]  # run -> tag -> meta


# --- /data/plugin/text/text ---
class TextDatum(BaseModel):
    wall_time: float
    step: int
    text: str


class TextDataResponse(BaseModel):
    __root__: List[TextDatum]


# --- Generic fallback for unknown/custom plugins ---
class GenericPluginResponse(BaseModel):
    __root__: Dict[str, Optional[Dict]]
