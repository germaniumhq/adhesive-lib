from typing import Dict, Union, List
from mypy_extensions import TypedDict


class BinaryDefinitionRequired(TypedDict):
    name: str
    platform: str


class BinaryDefinition(BinaryDefinitionRequired, total=False):
    docker_tag: str
    version_manager: str
    publish_pypi: str


class PipelineConfigRequired(TypedDict):
    repo: Union[List[str], str]
    binaries: Dict[str, Union[BinaryDefinition, List[BinaryDefinition]]]


class PipelineConfig(PipelineConfigRequired, total=False):
    # the name and the version are read using distutils.core
    name: str
    version: str

    # the rest are passed from the build configuration
    run_flake8: bool
    run_mypy: bool
    run_black: bool
    run_version_manager: bool
    version_manager: str


class PipelineToken:
    build: PipelineConfig

