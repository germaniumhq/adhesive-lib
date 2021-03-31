import os
from typing import Optional

import adhesive

from germanium_nodejs.pipeline_types import PipelineConfig
from germanium_nodejs.steps import noop

noop()




def pipeline(config: Optional[PipelineConfig] = None) -> None:
    script_dir = os.path.dirname(__file__)

    adhesive.bpmn_build(
        os.path.join(script_dir, "build_node.bpmn"),
        initial_data={})
