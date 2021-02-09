import adhesive
import ge_git
from adhesive import scm


class Data:
    release: bool


@adhesive.task('Checkout code')
def checkout_code(context: adhesive.Token[Data]):
    scm.checkout(context.workspace)


@adhesive.task('Fetch Dependencies')
def fetch_dependencies(context: adhesive.Token[Data]):
    context.workspace.run(f"""
        rm -fr node_modules
        yarn
    """)


@adhesive.task('Yarn Build')
def yarn_build(context: adhesive.Token[Data]) -> None:
    context.workspace.run("""
        yarn build
    """)


@adhesive.task('Read Metadata')
def read_metadata(context: adhesive.Token[Data]) -> None:
    context.data.release = ge_git.is_release()


@adhesive.task('Patch versions')
def patch_versions(context: adhesive.Token[Data]) -> None:
    context.workspace.run("""
        vm
    """)


@adhesive.task('Push source + tags on git server')
def push_source_tags_on_git_server(context: adhesive.Token[Data]) -> None:
    context.workspace.run("""
        git push
        git push --tags
    """)


@adhesive.task('Publish Release on npm')
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