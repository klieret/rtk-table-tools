#!/usr/bin/env python3

# std
from typing import Union, List
from pathlib import Path, PurePath

# 3rd
import pandas as pd
import numpy as np


class Kanjis(object):
    def __init__(self, path: Union[str, PurePath], edition=6):
        path = Path(path)
        self.edition = edition
        self.df = self._read(path)

    def _read(self, path: Path) -> pd.DataFrame:
        with path.open("r") as csvfile:
            df = pd.read_csv(csvfile, comment="#")
        df["id"] = df["id_{}th_ed".format(self.edition)]
        df["id"].fillna(0, inplace=True)
        df["id"] = df["id"].astype(np.int16)
        df.drop(columns=["id_5th_ed", "id_6th_ed"], inplace=True)
        df["components"].fillna("", inplace=True)
        df["on_reading"].fillna("", inplace=True)
        df["kun_reading"].fillna("", inplace=True)
        df["on_reading"] = df["on_reading"].str.split(";")
        df["kun_reading"] = df["kun_reading"].str.split(";")
        return df

    @property
    def kanjis(self) -> List[str]:
        return self.df["kanji"].values.tolist()

    @property
    def ids(self) -> List[str]:
        return self.df["id"].values.tolist()


class LatexKanjiTable(object):
    def __init__(self, k):
        self.ncols = 8
        self.nrows = 10
        self.k = k
        self.cell_width = "2.5cm"
        self.vadd = "0.3cm"

    def _begin_table(self):
        r = r"\begin{longtable}{|" + "c|" * self.ncols + r"}" + "\n"
        r += "\\hline\n"
        return r

    def _end_table(self):
        # r = "\\hline\n"
        r = r"\end{longtable}" + "\n"
        return r

    def _format_cell_content(self, content):
        r = "\\begin{{minipage}}{{{}}}".format(self.cell_width) + "\n"
        r += r"\centering" + "\n"
        r += "\\vspace{{{}}}\n".format(self.vadd)
        r += r"{\Huge " + content[0] + r"}"
        r += "\\\\[0.3ex]\n" + str(content[1]) + "\n"
        r += "\\vspace{{{}}}\n".format(self.vadd)
        r += r"\end{minipage}" + "\n"
        return r

    def _cell(self, content, icol):
        if icol < self.ncols - 1:
            return self._format_cell_content(content) + "&"
        else:
            return self._format_cell_content(content) + "\\\\ \\hline"

    def generate(self):
        out = self._begin_table()
        content = zip(self.k.kanjis, self.k.ids)
        for i, cell in enumerate(content):
            icol = i % self.ncols
            out += self._cell(cell, icol)
        out += "\n"
        out += self._end_table()
        return out


if __name__ == "__main__":
    k = Kanjis("data/kanjis.csv")
    lt = LatexKanjiTable(k)
    # lt.ncols = 10
    with open("build/table.tex", "w") as outfile:
        outfile.write(lt.generate())
