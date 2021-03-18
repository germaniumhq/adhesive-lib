import os
import re

import adhesive
from adhesive import scm
from adhesive.secrets import secret
from adhesive.workspace import docker

import gbs
import ge_git
import ge_tooling
from germanium_py_exe.pipeline_types import BinaryDefinition, PipelineToken

current_folder = os.path.abspath(os.curdir)
sources_folder = ge_git.find_parent_git_folder(current_folder)


@adhesive.task('Prepare build')
def prepare_build(context):
    pass


@adhesive.task('Checkout Code')
def checkout_code(context):
    scm.checkout(context.workspace)


@adhesive.task(re='Ensure tool: (.*)')
def ensure_tool(context, tool_name: str) -> None:
    ge_tooling.ensure_tooling(context, tool_name)


@adhesive.task('Run tool: version-manager')
def run_tool_version_manager(context):
    ge_tooling.run_tool(
        context,
        tool="version-manager",
        command="version-manager",
        mount=sources_folder,
        pwd=current_folder)


@adhesive.task('Run flake8')
def run_flake8(context):
    ge_tooling.run_tool(context, tool="flake8", command=f"""
        flake8 .
    """)


@adhesive.task('Run mypy')
def run_mypy(context):
    # the shadow-file is a W/A (hack) so we don't get to mypy the
    # _adhesive build itself, since that would be checked by adhesive
    # itself
    ge_tooling.run_tool(context, tool="mypy", command="""
        export MYPYPATH=./stubs:.
        mypy --shadow-file _adhesive.py setup.py .
    """)


@adhesive.task('Run black')
def run_black(context):
    ge_tooling.run_tool(context, tool="black", command="""
        black --check .
    """)


@adhesive.task('GBS Test {loop.value.name}')
def gbs_test(context: adhesive.Token):
    binary: BinaryDefinition = context.loop.value
    image_name = gbs.test(context,
                          platform=binary.platform)

    # if we don't have gbs-test.py we're done
    try:
        context.workspace.run("ls gbs-test.py")
    except Exception:
        return

    # if we do, we launch it
    context.workspace.run(f"python gbs-test.py {image_name}")


@adhesive.task('GBS Build {loop.value.name}')
def gbs_build(context):
    binary: BinaryDefinition = context.loop.value
    binary.docker_image = gbs.build(context, platform=binary.platform)


@adhesive.gateway('Is release version?')
def is_release_version_(context: adhesive.Token[PipelineToken]):
    if context.data.build.run_version_manager:
        context.workspace.pwd = current_folder

        current_version = ge_tooling.run_tool(
            context,
            tool="version-manager",
            command="version-manager --tag",  # this uses git to fetch info
            mount=sources_folder,
            pwd=current_folder,
            capture_stdout=True,).strip()

        current_branch = context.workspace.run(
            """
                git rev-parse --abbrev-ref HEAD
            """,
            capture_stdout=True).strip()
    else:
        current_version = ge_tooling.run_tool(
            context,
            tool="version-manager",
            command="version-manager --display latest",
            capture_stdout=True).strip()
        current_branch = "master"

    context.data.release_version = ge_git.get_tag_version(current_version)
    context.data.master_branch = ge_git.is_master_branch(current_branch)


@adhesive.task('Find published binaries')
def find_published_binaries(context):
    context.data.published_binaries = [
            binary for binary in context.data.build.binaries if binary.publish_pypi ]


@adhesive.task(re='Publish on (.*)$')
def publish_on_nexus(context, registry):
    if registry not in {'pypitest', 'pypimain', 'nexus', 'pypi'}:
        raise Exception("You need to pass a server from pypitest, pypimain or nexus")

    credentials_file = "PYPIRC_LOCAL_NEXUS" if registry == "nexus" else "PYPIRC_RELEASE_FILE"
    binary = context.loop.value

    with docker.inside(
            context.workspace,
            binary.docker_image) as docker_workspace:
        with secret(docker_workspace,
                    credentials_file,
                    "/germanium/.pypirc"):
            if binary.publish_pypi == "sdist":
                docker_workspace.run(f"""
                    cd /src
                    python setup.py sdist upload -r {registry}
                """)
            elif binary.publish_pypi == "bdist":
                docker_workspace.run(f"""
                    cd /src
                    python setup.py bdist_wheel upload -r {registry}
                """)
            else:
                raise Exception("Publishing can only be sdist or bdist")


@adhesive.task('Publish binary on germaniumhq.com')
def publish_binary_on_germaniumhq_com(context):
    raise Exception("not implemented")


def parse_url(url: str) -> str:
    """
    Extracts the name of a git repository.
    """
    GIT_URL_PATTERN = re.compile(r"(.*?\:\/\/)?(.*?@)?(.+?)(\:.+)?\/.*")
    m = GIT_URL_PATTERN.match(url)

    if not m:
        raise Exception(f"Unable to parse git url {url}")

    return str(m.group(3))


@adhesive.task('Push sources + tags to {loop.value}')
def push_sources_tags_to_loop_value_(context):
    print("remove me")
    return

    git_url = context.loop.value
    server_name = parse_url(git_url)

    with docker.inside(
            context.workspace,
            ge_tooling.image_name("git")) as docker_workspace:
        docker_workspace.run("""
            mkdir /germanium/.ssh
            chmod 711 /germanium/.ssh
        """)

        with secret(docker_workspace,
                    "GITHUB_JENKINS_PUBLISH_KEY",
                    "/germanium/.ssh/id_rsa"):
            docker_workspace.run("""
                chmod 600 /germanium/.ssh/id_rsa
            """)

            docker_workspace.run(f"""
                ssh-keyscan {server_name} >> /germanium/.ssh/known_hosts
                git remote add {server_name} {context.loop.value} || true
                git push {server_name} HEAD:master
            """)

