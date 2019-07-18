#!/usr/bin/env ptyhon3

# std
from pathlib import Path, PurePath
from typing import Union, Optional, List
from abc import ABC, abstractmethod
import inspect

# 3rd
import numpy as np


class AbstractKanjiPoster(ABC):
    def __init__(self, k):
        self.k = k
        self.ncols = 9

    @abstractmethod
    def _begin_document(self) -> str:
        pass

    @abstractmethod
    def _end_document(self) -> str:
        pass

    @abstractmethod
    def _begin_table(self) -> str:
        pass

    @abstractmethod
    def _end_table(self) -> str:
        pass

    @abstractmethod
    def _format_cell(self, cell, icol: int) -> str:
        pass

    def generate(self, path: Optional[Union[str, PurePath]] = None) -> str:
        if path is not None:
            path = Path(path)
        out = self._begin_document()
        out += self._begin_table()
        for i, cell in enumerate(self.k):
            icol = i % self.ncols
            out += self._format_cell(cell, icol)
        out += "\n"
        out += self._end_table()
        out += self._end_document()
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w") as outfile:
                outfile.write(out)
        return out


class DefaultKanjiPoster(AbstractKanjiPoster):
    def __init__(self, k):
        super().__init__(k)
        self.nrows = 10
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

    def _get_color(self, kanji) -> str:
        return self.jlpt_colors[kanji.jlpt]

    def _begin_document(self) -> str:
        return inspect.cleandoc(r"""
        \documentclass[]{article}
        \usepackage[margin=1cm,a3paper]{geometry}
        \usepackage{xeCJK}
        \setCJKmainfont[BoldFont=AozoraMincho-bold,AutoFakeSlant=0.15]{Aozora Mincho}
        \usepackage{xcolor}
        \usepackage{longtable}
        \pagenumbering{gobble}  % no page numbers
        \begin{document}
        """)

    def _end_document(self) -> str:
        return r"""
        \end{document}
        """

    def _begin_table(self) -> str:
        col_line = ""
        row_line = ""
        if self.grid:
            col_line = "|"
            row_line = "\\hline"
        cols_str = col_line + ("c" + col_line) * self.ncols
        return "\\begin{{longtable}}{{{cols}}}\n" \
               "{row_line}\n".format(cols=cols_str, row_line=row_line)

    def _end_table(self) -> str:
        return r"\end{longtable}" + "\n"

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
        return "\\begin{{minipage}}[c][{dim}][c]{{{dim}}}\\centering\\scalebox{{{scale}}}{{{kanji}}}\\end{{minipage}}\n".format(
            kanji=kanji.kanji,
            scale=self.kanji_scale,
            dim=self.kanji_box_width_height
        )

    def _format_cell_content(self, kanji):

        return "\\begin{{minipage}}{{{width}}}\n" \
               "\\centering\n" \
               "\\color[HTML]{{{color}}}" \
               "\\vspace{{{vadd}}}\n" \
               "{kanji_header}{kanji}{kanji_footer}" \
               "\\vspace{{{vadd}}}\n" \
               "\\end{{minipage}}\n".format(
            width=self.cell_width,
            vadd=self.vadd,
            color=self._get_color(kanji),
            kanji_header=self._format_kanji_header(kanji),
            kanji_footer=self._format_kanji_footer(kanji),
            kanji=self._format_kanji(kanji)
        )

    def _format_cell(self, content, icol: int) -> str:
        if icol < self.ncols - 1:
            return self._format_cell_content(content) + "&"
        else:
            line = ""
            if self.grid:
                line = "\\hline"
            return self._format_cell_content(content) + "\\\\ " + line


class MinimalistKanjiPoster(DefaultKanjiPoster):
    def _format_kanji_footer(self, kanji):
        return ""

    def _format_kanji_header(self, kanji):
        return ""


_name2class = {
    "default": DefaultKanjiPoster,
    "minimalist": MinimalistKanjiPoster
}


def poster_by_name(name: str, kanji, **kwargs) -> AbstractKanjiPoster:
    return _name2class[name](kanji, **kwargs)


def get_available_poster_styles() -> List[str]:
    return sorted(list(_name2class.keys()))