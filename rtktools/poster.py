#!/usr/bin/env ptyhon3

# std
from pathlib import Path, PurePath
from typing import Union, Optional, List
from abc import ABC, abstractmethod
import inspect
import collections

# 3rd
import numpy as np

# ours
from rtktools.util.log import log
from rtktools.latex import LatexTableDocument


class AbstractKanjiPoster(ABC):
    def __init__(self, k):
        self.k = k

    @abstractmethod
    def generate(self, path: Optional[Union[str, PurePath]] = None) -> str:
        pass

    @abstractmethod
    def set_options(self, *args):
        pass


class DefaultKanjiPoster(LatexTableDocument, AbstractKanjiPoster):
    def __init__(self, k):
        AbstractKanjiPoster.__init__(self, k)
        LatexTableDocument.__init__(self)
        self.cell_width = "2.5cm"
        self.vadd = "0.3cm"
        self.grid = True
        self.jlpt_colors = {
            0: "D8102C",
            1: "831378",
            2: "435E7A",
            3: "435E7A",
            4: "007F51",
            5: "007F51"
        }
        self.kanji_scale = 6
        self.kanji_box_width_height = "2.1cm"
        self.paper_format = "a3paper"
        self.page_margin = "1cm"
        self.ncols = 9
        self.grid = True


    def _get_contents(self):
        return self.k

    def set_options(self, options):
        for option in options:
            self.set_option(option)

    def set_option(self, option):
        if option == "no-grid":
            self.grid = False
        elif option == "no-colors":
            self.jlpt_colors = collections.defaultdict(lambda: "000000")
        else:
            log.warning("Unknown option '{}'".format(option))


    def _get_color(self, kanji) -> str:
        return self.jlpt_colors[kanji.jlpt]

    def _format_kanji_header(self, kanji):
        jlpt_str = ""
        if int(kanji.jlpt) > 0:
            jlpt_str = "JLPT{}".format(kanji.jlpt)
        freq_str = ""
        if not np.isnan(kanji.freq) and int(kanji.freq):
            freq_str = "\\#{}".format(int(kanji.freq))
        return "{{ \\small {jlpt_str} {freq_str} }}$\\ \\!\\!\\!$\\\\ \n".format(
            jlpt_str=jlpt_str, freq_str=freq_str
        )

    def _format_kanji_footer(self, kanji):
        return "\\\\[0.3ex]\n {{ \\small {id} {utf} }}\n".format(
            id=kanji.heisig_id, utf=kanji.utf
        )

    def _format_kanji(self, kanji):
        return inspect.cleandoc("""\\begin{{minipage}}[c][{dim}][c]{{{dim}}}
            \\centering
            \\scalebox{{{scale}}}{{{kanji}}}
            \\end{{minipage}}\n""".format(
            kanji=kanji.kanji,
            scale=self.kanji_scale,
            dim=self.kanji_box_width_height
        ))

    def _format_cell_content(self, kanji):

        if kanji is None:
            return ""

        return inspect.cleandoc("""\\begin{{minipage}}{{{width}}}\n
            \\centering\n
            \\color[HTML]{{{color}}}\\vspace{{{vadd}}}\n
            {kanji_header}
            {kanji}
            {kanji_footer}
            \\vspace{{{vadd}}}\n
            \\end{{minipage}}\n""".format(
            width=self.cell_width,
            vadd=self.vadd,
            color=self._get_color(kanji),
            kanji_header=self._format_kanji_header(kanji),
            kanji_footer=self._format_kanji_footer(kanji),
            kanji=self._format_kanji(kanji)
        ))


class SmallKanjiPoster(DefaultKanjiPoster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ncols = 15
        self.cell_width = "1.4cm"
        self.vadd = "0.15cm"
        self.kanji_scale = 2.5
        self.kanji_box_width_height = "0.9cm"

    def _format_kanji_header(self, kanji):
        return "{{ \\footnotesize {utf} }}".format(utf=kanji.utf)

    def _format_kanji_footer(self, kanji):
        return "\\\\[0.3ex]\n {{ \\small {id} }}\n".format(
            id=kanji.heisig_id, utf=kanji.utf
        )


class SmallA4KanjiPoster(SmallKanjiPoster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paper_format = "a4paper"
        self.ncols = 10


class DefaultA4KanjiPoster(DefaultKanjiPoster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paper_format = "a4paper"
        self.ncols = 6


class MinimalistKanjiPoster(DefaultKanjiPoster):
    def _format_kanji_footer(self, kanji):
        return ""

    def _format_kanji_header(self, kanji):
        return ""


class MinimalistA4KanjiPoster(MinimalistKanjiPoster, DefaultA4KanjiPoster):
    pass


class MinimalistSmallKanjiPoster(MinimalistKanjiPoster, SmallKanjiPoster):
    pass


class MinimalistSmallA4KanjiPoster(MinimalistKanjiPoster, SmallA4KanjiPoster):
    pass


_name2class = {
    "default": DefaultKanjiPoster,
    "small": SmallKanjiPoster,
    "small-a4": SmallA4KanjiPoster,
    "default-a4": DefaultA4KanjiPoster,
    "minimalist": MinimalistKanjiPoster,
    "minimalist-a4": MinimalistA4KanjiPoster,
    "minimalist-small": MinimalistSmallKanjiPoster,
    "minimalist-small-a4": MinimalistSmallA4KanjiPoster
}


def poster_by_name(name: str, kanji, **kwargs) -> AbstractKanjiPoster:
    return _name2class[name.lower()](kanji, **kwargs)


def get_available_poster_styles() -> List[str]:
    return sorted(list(_name2class.keys()))