import textwrap


tools = {
    "mypy": textwrap.dedent("""\
        FROM germaniumhq/python:3.7
        ENV REFRESHED_AT 2018.10.14-06:56:31
        RUN pip install mypy
        """),

    "ansible": textwrap.dedent("""\
        FROM germaniumhq/python:3.7
        ENV REFRESHED_AT 2018.10.14-06:58:16
        RUN pip install ansible
    """),

    "flake8": textwrap.dedent("""\
        FROM germaniumhq/python:3.7
        ENV REFRESHED_AT 2018.10.14-06:56:31
        RUN pip install flake8
    """),

    "python": textwrap.dedent("""\
        FROM germaniumhq/python:3.7
    """),

    "behave": textwrap.dedent("""\
        FROM python:3.7

        RUN pip install behave
        RUN curl https://get.docker.com | sh
    """),

    "git": textwrap.dedent("""\
        FROM germaniumhq/ubuntu:18.04
        ENV REFRESHED_AT 2018.10.18-05:25:08
        USER root
        RUN apt update -y && apt install -y git && rm -rf /var/lib/apt/lists/*
        USER germanium
    """),

    "version-manager": textwrap.dedent("""\
        FROM bmst/version-manager:2.5.0
    """)
}


@adhesive.task(r"^Ensure Tooling:\s+(.+)$")
def ensure_tooling(context, tool_name) -> None:
    w = context.workspace

    with w.temp_folder():
        w.write_file("Dockerfile", tools[tool_name])
        w.run(f"docker build -t germaniumhq/tools-{tool_name}:latest .")


@adhesive.task("^Run tool: (.*?)$")
def run_tool(context, command: str) -> None:
    tool_name = command.split(" ")[0]

    with docker.inside(context.workspace,
                       f"germaniumhq/tools-{tool_name}") as w:
        w.run(command)

