#!/usr/bin/env python3

# std
from typing import List, Union
from pathlib import PurePath, Path

# 3rd
import pandas as pd
import numpy as np


class KanjiCollection(object):
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