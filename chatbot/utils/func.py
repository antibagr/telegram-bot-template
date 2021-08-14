"""
Helpful functions without any dependencies
"""

import json

from typing import Optional, Iterable


def tag(string: str, tag_name: Optional[str] = "pre") -> str:
    """
    Format a string to HTML tag which defaults to "pre" (code styling)

    :param str string: String to be tagged
    :param Optional[str] tag_name: . Defaults to "pre".

    """
    return f"<{tag_name}>{str(string)}</{tag_name}>"


def to_json(message: Iterable, add_tag: bool = True) -> str:
    """
    Convert any object that can be dumped to json to string.
    By default it will be wrapper to HTML <pre> tag
    You can specify to return untagged content if set add_tag = False

    :param Iterable message: .
    :param bool add_tag: . Defaults to True.

    """
    dump = json.dumps(dict(message), indent=4, sort_keys=True, ensure_ascii=False)
    return tag(dump) if add_tag else dump
