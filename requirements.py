import re

from typing import Iterable, Tuple, List, Pattern, Match


__all__ = [
    "Requirements",
    "read",
]


class Requirements:
    __slots__ = (
        "_install_requires",
        "_dependency_links",
    )

    def __init__(
        self,
        install_requires: Iterable[str],
        dependency_links: Iterable[str],
    ) -> None:
        self._install_requires: Tuple[str, ...] = tuple(install_requires)
        self._dependency_links: Tuple[str, ...] = tuple(dependency_links)

    @property
    def install_requires(self) -> List[str]:
        return list(self._install_requires)

    @property
    def dependency_links(self) -> List[str]:
        return list(self._dependency_links)


def read(file: str) -> Requirements:
    git_pattern: Pattern = re.compile(r"^(.*/([0-9a-zA-Z_]+).git@v(\d+\.\d+\.\d+))(#.*)?$")

    with open(file=file, mode="r") as stream:
        text: str = stream.read()
    lines: List[str] = [line for line in (line.strip() for line in text.split("\n")) if line and not line.startswith("#")]
    matches: List[Match] = [re.match(git_pattern, line) for line in lines]
    install_other_requires: List[str] = [line for match, line in zip(matches, lines) if not match]
    install_git_requires: List[str] = [
        "{}=={}".format(match.group(2), match.group(3))
        for match, line in zip(matches, lines) if match
    ]
    dependency_links: List[str] = [
        "{}#egg={}-{}".format(match.group(1), match.group(2), match.group(3))
        for match, line in zip(matches, lines) if match
    ]
    return Requirements(
        install_requires=install_other_requires + install_git_requires,
        dependency_links=dependency_links,
    )
