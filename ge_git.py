import re

TAG_VERSION = re.compile("^\\d+\\.\\d+(\\.\\d+)?$")


def is_master_branch(version: str) -> bool:
    return version == "master"


def is_tag_version(version: str) -> bool:
    return TAG_VERSION.match(version)

