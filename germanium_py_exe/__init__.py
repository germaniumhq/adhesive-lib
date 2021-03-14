import adhesive
import os
import addict  # type: ignore

from germanium_py_exe.pipeline_types import PipelineConfig
from germanium_py_exe.steps import *  # type: ignore


def pipeline(build: PipelineConfig) -> None:
    script_dir = os.path.dirname(__file__)

    build_data = addict.Dict(build)

    if "run_mypy" not in build_data:
        build_data.run_mypy = True

    if "run_flake8" not in build_data:
        build_data.run_flake8 = True

    if "run_black" not in build_data:
        build_data.run_black = True

    if "run_version_manager" not in build_data:
        build_data.run_version_manager = True

    if build_data.repo and not isinstance(build_data.repo, list):
        build_data.repo = [ build_data.repo ]

    if not isinstance(build_data.binaries, list):
        build_data.binaries = [ build_data.binaries ]

    adhesive.bpmn_build(
        os.path.join(script_dir, "build_python.bpmn"),
        initial_data={
            "build": build_data
        })

