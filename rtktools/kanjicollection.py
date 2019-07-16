#!/usr/bin/env python3

# std
from typing import List, Union, Optional
from pathlib import PurePath, Path

# 3rd
import pandas as pd
import numpy as np


class KanjiCollection(object):
    def __init__(self,
                 path: Union[str, PurePath],
                 tangorin_path: Optional[Union[str, PurePath]] = None,
                 edition=6):
        path = Path(path)
        tangorin_path = Path(tangorin_path)
        self.edition = edition
        self.df = self._read(path)
        if tangorin_path:
            self._read_tangorin(tangorin_path)

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

    def _read_tangorin(self, path: Path):
        with path.open("r") as csvfile:
            df = pd.read_csv(csvfile, comment="#")
        # self.df["ord"] = self.df["kanji"].apply(ord)
        self.df = self.df.merge(df, left_on="kanji", right_on="kanji")
        self.df["jlpt"].fillna(0, inplace=True)
        self.df["jlpt"] = self.df["jlpt"].astype(np.int8)

    def __iter__(self):
        return self.df.itertuples()

    @property
    def kanjis(self) -> List[str]:
        return self.df["kanji"].values.tolist()