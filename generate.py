#!/usr/bin/env python3

# std
from typing import Union, List
from pathlib import Path, PurePath
import requests
import time
import json
import collections

# 3rd
import pandas as pd
import numpy as np
from tqdm.auto import tqdm
from bs4 import BeautifulSoup


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


class TangorinScraper(object):
    def __init__(self, out_dir="scrape"):
        self.out_dir = Path(out_dir)

    def _build_url(self, kanji):
        return "https://tangorin.com/kanji?search={}".format(kanji)

    @staticmethod
    def _download(url: str, path: Path) -> None:
        with path.open("wb") as outfile:
            r = requests.get(url)
            outfile.write(r.content)

    def download_kanji(self, kanji: str, force=False) -> bool:
        path = self.out_dir / (str(ord(kanji)) + ".html")
        if not force and path.exists():
            tqdm.write("Skipping existing kanji {}".format(kanji))
            return False
        self._download(self._build_url(kanji), path)
        return True

    def download_kanjis(self, kanjis: List[str], timeout=3):
        for kanji in tqdm(kanjis):
            new_download = self.download_kanji(kanji)
            if new_download:
                time.sleep(timeout)


class TangorinParser(object):
    def __init__(self):
        pass

    def parse(self, path):
        path = Path(path)
        with path.open("r") as infile:
            html = infile.read()
        soup = BeautifulSoup(html, "html.parser")
        for _script in soup.find_all("script"):
            if not _script.string:
                continue
            if "window.__PRELOADED_STATE" in _script.string:
                script = _script.string
                break
        else:
            return {}
        _, dct_str = script.split("window.__PRELOADED_STATE=")
        dct_str = dct_str[:-1]  # split ;
        dct = json.loads(dct_str)
        dct = dct["search"][list(dct["search"].keys())[0]]["items"][0]["rows"][0]
        out_dct = {}
        renames = {
            "jlpt": "jlpt",
            "k": "kanji"
        }
        for old, new in renames.items():
            try:
                out_dct[new] = dct[old]
            except KeyError:
                out_dct[new] = None
        return out_dct

    def parse_dir(self, folder):
        folder = Path(folder)
        dct = collections.defaultdict(list)
        for file in tqdm(list(folder.iterdir())):
            if not file.is_file():
                continue
            for key, value in self.parse(file).items():
                dct[key].append(value)
        return dct

    def save2csv(self, dct, path="tangorin.csv"):
        path = Path(path)
        df = pd.DataFrame(dct)
        df.to_csv(path)


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


if __name__ == "__main__":
    k = Kanjis("data/kanjis.csv")
    lt = LatexKanjiTable(k)
    # ts = TangorinScraper()
    # ts.download_kanjis(k.kanjis)
    tp = TangorinParser()
    tp.save2csv(tp.parse_dir("scrape/"))
    # lt.ncols = 10
    # with open("build/table.tex", "w") as outfile:
    #     outfile.write(lt.generate())
