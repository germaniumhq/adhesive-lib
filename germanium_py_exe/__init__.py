import adhesive
import os
from germanium_py_exe import steps
import addict

from .pipeline_types import PipelineConfig


def pipeline(build: PipelineConfig) -> None:
    script_dir = os.path.dirname(__file__)

    build = addict.Dict(build)

    if not "run_mypy" in build:
        build.run_mypy = True

    if not "run_flake8" in build:
        build.run_flake8 = True

    if build.repo and not isinstance(build.repo, list):
        build.repo = [ build.repo ]

    if not isinstance(build.binaries, list):
        build.binaries = [ build.binaries ]

    adhesive.bpmn_build(
        os.path.join(script_dir, "build_python.bpmn"),
        initial_data={
            "build": build
        })

