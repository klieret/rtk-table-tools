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

    @abstractmethod
    def generate(self, path: Optional[Union[str, PurePath]] = None) -> str:
        pass


class DefaultKanjiPoster(AbstractKanjiPoster):
    def __init__(self, k):
        super().__init__(k)
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

    def generate(self, path: Optional[Union[str, PurePath]] = None) -> str:
        if path is not None:
            path = Path(path)
        out = self._begin_document()
        out += self._begin_table()
        for i, cell in enumerate(self.k):
            icol = i % self.ncols
            out += self._format_cell(cell, icol)
        for icol in range(len(self.k) % self.ncols, self.ncols):
            out += self._format_cell(None, icol)
        out += "\n"
        out += self._end_table()
        out += self._end_document()
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w") as outfile:
                outfile.write(out)
        return out

    def _get_color(self, kanji) -> str:
        return self.jlpt_colors[kanji.jlpt]

    def _begin_document(self) -> str:
        return inspect.cleandoc("""
        \\documentclass[]{{article}}
        \\usepackage[margin={margin},{paper}]{{geometry}}
        \\usepackage{{xeCJK}}
        \\setCJKmainfont[BoldFont=AozoraMincho-bold,AutoFakeSlant=0.15]{{Aozora Mincho}}
        \\usepackage{{xcolor}}
        \\usepackage{{longtable}}
        \\pagenumbering{{gobble}}  % no page numbers
        \\begin{{document}}
        """.format(
            paper=self.paper_format,
            margin=self.page_margin
        ))

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

    def _format_cell(self, content, icol: int) -> str:
        if icol < self.ncols - 1:
            return self._format_cell_content(content) + "&"
        else:
            line = ""
            if self.grid:
                line = "\\hline"
            return self._format_cell_content(content) + "\\\\ " + line


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