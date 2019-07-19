#!/usr/bin/env python3

# std
from abc import ABC, abstractmethod
from typing import Optional, Union, List
from pathlib import PurePath

# ours
from rtktools.util.log import log
from rtktools.latex import LatexTableDocument


class AbstractSolutions(ABC):
    def __init__(self, k):
        self.k = k

    @abstractmethod
    def generate(self, path: Optional[Union[str, PurePath]] = None) -> str:
        pass

    @abstractmethod
    def set_options(self, *args):
        pass


class DefaultSolutions(LatexTableDocument, AbstractSolutions):
    def __init__(self, k):
        AbstractSolutions.__init__(self, k)
        LatexTableDocument.__init__(self)
        self.cell_width = "4cm"
        self.ncols = 6

    def _get_contents(self):
        return self.k

    def set_options(self, options):
        for option in options:
            self.set_option(option)

    def set_option(self, option):
        log.warning("Unknown option '{}'".format(option))

    def _format_cell_content(self, kanji):
        if kanji is None:
            return ""
        return """\\begin{{minipage}}{{{width}}}\n
            {id} ({kanji}): {keyword}\n
            \\end{{minipage}}""".format(
            id=kanji.heisig_id,
            kanji=kanji.kanji,
            keyword=kanji.keyword,
            width=self.cell_width
        )


_name2class = {
    "default": DefaultSolutions,
}


def solution_by_name(name: str, kanji, **kwargs) -> AbstractSolutions:
    return _name2class[name.lower()](kanji, **kwargs)


def get_available_solution_styles() -> List[str]:
    return sorted(list(_name2class.keys()))