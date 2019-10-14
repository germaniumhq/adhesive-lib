import adhesive
from adhesive import scm
from adhesive.workspace import docker

import ge_tooling  # this defines the Ensure Tooling, and Run tool steps.


@adhesive.task("Checkout Code")
def checkout_code(context) -> None:
    scm.checkout(context.workspace)


@adhesive.task(r"^Ensure Tooling:\s+(.+)$")
def ensure_tooling(context, tool_name) -> None:
    ge_tooling.ensure_tooling(context, tool_name)


@adhesive.task("^Run Tool: (.*?)$")
def run_tool(context,
             command: str) -> str:
    ge_tooling.run_tool(context, command)


@adhesive.task("Fetch Base Images")
def fetch_base_images(context) -> None:
    pass


@adhesive.task(
        "Create Base Container Image .*?",
        "Create Build Container Image .*?",
)
def build_docker_image(context) -> None:
    with context.workspace.chdir(context.loop.key):
        docker.build(context.workspace,
                     context.loop.value)


@adhesive.task("Test Containers")
def test_containers(context) -> None:
    with docker.inside(context.workspace,
                       f"germaniumhq/tools-{tool_name}") as w:
        w.run("behave")


@adhesive.task("Push Containers")
def push_containers(context) -> None:
    pass


def pipeline_build_gbs_images(config):
    adhesive.process_start()\
        .branch_start()\
            .task("Checkout Code")\
            .task("Fetch Base Images")\
        .branch_end()\
        .branch_start()\
            .task("Ensure Tooling: behave")\
        .branch_end()\
        .sub_process_start("Base Containers")\
            .task("Create Base Container Image {loop.key}", loop="data.base_containers")\
        .sub_process_end()\
        .sub_process_start("Base Containers")\
            .task("Create Build Container Image {loop.key}", loop="data.build_containers")\
        .sub_process_end()\
        .task("Run Tool: behave")\
        .task("Push Containers")\
    .process_end()\
    .build(initial_data=config)

