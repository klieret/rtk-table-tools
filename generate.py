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
        df["utf"] = df["kanji"].apply(lambda x: "u" + hex(ord(x))[2:])
        return df

    def __iter__(self):
        return self.df.itertuples()

    @property
    def kanjis(self) -> List[str]:
        return self.df["kanji"].values.tolist()


class LatexKanjiTable(object):
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
               "{{\Huge {kanji} }}\n" \
               "\\\\[0.3ex]\n" \
               "{id}\n" \
               "\\vspace{{{vadd}}}\n" \
               "\\end{{minipage}}\n".format(
            width=self.cell_width,
            vadd=self.vadd,
            kanji=content.kanji,
            id=content.id
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


if __name__ == "__main__":
    k = Kanjis("data/kanjis.csv")
    lt = LatexKanjiTable(k)
    # lt.ncols = 10
    with open("build/table.tex", "w") as outfile:
        outfile.write(lt.generate())
