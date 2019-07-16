#!/usr/bin/env ptyhon3


class KanjiPoster(object):
    def __init__(self, k):
        self.ncols = 8
        self.nrows = 10
        self.k = k
        self.cell_width = "2.5cm"
        self.vadd = "0.3cm"

    def _begin_table(self):
        cols_str = "|" + "c|" * self.ncols
        return "\\begin{{longtable}}{{{cols}}}\n" \
               "\\hline\n".format(cols=cols_str)

    def _end_table(self):
        return r"\end{longtable}" + "\n"

    def _format_cell_content(self, content):
        return "\\begin{{minipage}}{{{width}}}\n" \
               "\\centering\n" \
               "\\vspace{{{vadd}}}\n" \
               "{{\\Huge {kanji} }}\n" \
               "\\\\[0.3ex]\n" \
               "{id} {utf}\n" \
               "\\vspace{{{vadd}}}\n" \
               "\\end{{minipage}}\n".format(
            width=self.cell_width,
            vadd=self.vadd,
            kanji=content.kanji,
            id=content.id,
            utf=content.utf
        )

    def _cell(self, content, icol):
        if icol < self.ncols - 1:
            return self._format_cell_content(content) + "&"
        else:
            return self._format_cell_content(content) + "\\\\ \\hline"

    def generate(self):
        out = self._begin_table()
        for i, cell in enumerate(self.k):
            icol = i % self.ncols
            out += self._cell(cell, icol)
        out += "\n"
        out += self._end_table()
        return out
