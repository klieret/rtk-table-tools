#!/usr/bin/env ptyhon3

# std
from pathlib import Path, PurePath
from typing import Union, Optional

# 3rd
import numpy as np


class KanjiPoster(object):
    def __init__(self, k):
        self.ncols = 8
        self.nrows = 10
        self.k = k
        self.cell_width = "2.5cm"
        self.vadd = "0.3cm"
        self.jlpt_colors = {
            0: "D8102C",
            1: "831378",
            2: "435E7A",
            3: "435E7A",
            4: "007F51",
            5: "007F51"
        }

    def _get_color(self, kanji) -> str:
        return self.jlpt_colors[kanji.jlpt]

    def _begin_table(self) -> str:
        cols_str = "|" + "c|" * self.ncols
        return "\\begin{{longtable}}{{{cols}}}\n" \
               "\\hline\n".format(cols=cols_str)

    @staticmethod
    def _end_table() -> str:
        return r"\end{longtable}" + "\n"

    def _format_cell_content(self, kanji):
        jlpt_str = ""
        if int(kanji.jlpt) > 0:
            jlpt_str = "JLPT{}".format(kanji.jlpt)
        freq_str = ""
        if not np.isnan(kanji.freq) and int(kanji.freq):
            freq_str = "\\#{}".format(int(kanji.freq))
        return "\\begin{{minipage}}{{{width}}}\n" \
               "\\centering\n" \
               "\\color[HTML]{{{color}}}" \
               "\\vspace{{{vadd}}}\n" \
               "{jlpt_str} {freq_str} $\ \!\!\!$\\\\ \n" \
               "{{\\Huge {kanji} }}\n" \
               "\\\\[0.3ex]\n" \
               "{id} {utf}\n" \
               "\\vspace{{{vadd}}}\n" \
               "\\end{{minipage}}\n".format(
            width=self.cell_width,
            vadd=self.vadd,
            kanji=kanji.kanji,
            id=kanji.id,
            utf=kanji.utf,
            color=self._get_color(kanji),
            jlpt_str=jlpt_str,
            freq_str=freq_str
        )

    def _cell(self, content, icol: int) -> str:
        if icol < self.ncols - 1:
            return self._format_cell_content(content) + "&"
        else:
            return self._format_cell_content(content) + "\\\\ \\hline"

    def generate(self, path: Optional[Union[str, PurePath]] = None) -> str:
        if path is not None:
            path = Path(path)
        out = self._begin_table()
        for i, cell in enumerate(self.k):
            icol = i % self.ncols
            out += self._cell(cell, icol)
        out += "\n"
        out += self._end_table()
        if path is not None:
            with path.open("w") as outfile:
                outfile.write(out)
        return out
