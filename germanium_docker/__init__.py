import adhesive

from germanium_docker.pipeline_types import ConfigDict


def pipeline(config: ConfigDict) -> None:
    import germanium_docker.steps

    """
    Builds the docker images
    """
    adhesive.build(initial_data={
        "build": config
    })
