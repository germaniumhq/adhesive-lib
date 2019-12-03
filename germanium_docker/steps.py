import adhesive
from adhesive import scm


@adhesive.task('Checkout Code')
def apt_install(context):
    scm.checkout(context.workspace)


@adhesive.task('Build Docker in {loop.key}', loop="build")
def apt_install(context):
    tags = context.loop.value

    if not isinstance(tags, list):
        tags = [tags]

    context.data.tags_to_push = set(tags)

    if not tags:
        raise Exception("Tags for tagging are needed in a docker build")

    context.workspace.run(f"""
        docker build -t {" -t ".join(tags)} {context.loop.key}
    """)


@adhesive.task('Push Docker Image {loop.key}', loop="tags_to_push")
def apt_install(context):
    context.workspace.run(f"""
        docker push {context.loop.key}
    """)
