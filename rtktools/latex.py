#!/usr/bin/env python3

# std
from typing import Optional, Union
from pathlib import PurePath, Path
import inspect
from abc import abstractmethod, ABC
from math import ceil


class LatexDocument(ABC):
    def __init__(self):
        self.paper_format = "a3paper"
        self.page_margin = "1cm"

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

    @abstractmethod
    def _generate_body(self):
        pass

    def generate(self, path: Optional[Union[str, PurePath]] = None) -> str:
        if path is not None:
            path = Path(path)
        out = self._begin_document()
        out += self._generate_body()
        out += self._end_document()
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w") as outfile:
                outfile.write(out)
        return out



class LatexTableDocument(LatexDocument):
    def __init__(self):
        super().__init__()
        self.ncols = 9
        self.grid = True

    @abstractmethod
    def _format_cell_content(self, content):
        pass

    @abstractmethod
    def _get_contents(self):
        pass

    def _generate_body(self):
        out = self._begin_table()
        for i, cell in enumerate(self._get_contents()):
            icol = i % self.ncols
            out += self._format_cell(cell, icol)
        for icol in range(len(self._get_contents()) % self.ncols, self.ncols):
            out += self._format_cell(None, icol)
        out += "\n"
        out += self._end_table()
        return out

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

    def _format_cell(self, content, icol: int) -> str:
        if icol < self.ncols - 1:
            return self._format_cell_content(content) + "&"
        else:
            line = ""
            if self.grid:
                line = "\\hline"
            return self._format_cell_content(content) + "\\\\ " + line


class LatexVerticalTableDocument(LatexTableDocument):
    def __init__(self):
        super().__init__()
        self.nrows = 50

    def _generate_body(self):
        out = self._begin_table()
        contents = self._get_contents()
        npages = ceil(len(contents) / self.ncols / self.nrows)

        for ipage in range(npages):
            for irow in range(self.nrows):
                for icol in range(self.ncols):
                    iitem = ipage * self.nrows * self.ncols + icol * self.nrows + irow
                    if iitem < len(contents):
                        out += self._format_cell(contents.df.loc[iitem], icol)
                    else:
                        out += self._format_cell(None, icol)
        out += "\n"
        out += self._end_table()
        return out
