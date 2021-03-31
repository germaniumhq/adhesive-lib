import os

import adhesive
import ge_git
import ge_tooling
from adhesive import scm
from germanium_nodejs.pipeline_types import Data
from cached_task import cached


current_folder = os.path.abspath(os.curdir)
sources_folder = ge_git.find_parent_git_folder(current_folder)


@adhesive.task('Checkout code')
def checkout_code(context: adhesive.Token[Data]):
    scm.checkout(context.workspace)


@adhesive.task('Fetch Dependencies')
@cached(
    inputs=[
        "package.json",
        "yarn.lock",
    ],
    outputs=[
        "node_modules/**/*"
    ]
)
def fetch_dependencies(context: adhesive.Token[Data]):
    context.workspace.run(f"""
        rm -fr node_modules
        yarn
    """)


@adhesive.task('Yarn Build')
@cached(
    inputs=[
        "*.json",
        "yarn.lock",
        "src/**",
        "?tests/**",
    ],
    outputs=[
        "?dist",
        "?build",
    ]
)
def yarn_build(context: adhesive.Token[Data]) -> None:
    context.workspace.run("""
        yarn build
    """)


@adhesive.task('Read Metadata')
def read_metadata(context: adhesive.Token[Data]) -> None:
    context.data.release = ge_git.is_release()
    context.data.version = ge_git.read_current_version_using_version_manager()


@adhesive.task('Patch versions')
def patch_versions(context: adhesive.Token[Data]) -> None:
    ge_tooling.run_tool(
        context,
        tool="version-manager",
        command="vm",
        mount=sources_folder,
        pwd=current_folder,
    )


@adhesive.task('Push source + tags on git server')
def push_source_tags_on_git_server(context: adhesive.Token[Data]) -> None:
    # FIXME: remove?
    # context.workspace.run("""
    #     git push
    #     git push --tags
    # """)
    pass


@adhesive.task('Publish Release on npm')
@cached(
    params="args[0].data.version",
)
def publish_release_on_npm(context: adhesive.Token[Data]) -> None:
    context.workspace.run("""
        npm publish --access public
    """)


def noop():
    """
    This method exists only so when optimizing imports, the import to this module,
    that defines the steps isn't removed.
    :return:
    """
    pass
