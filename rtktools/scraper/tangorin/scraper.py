#!/usr/bin/env python3

# std
from pathlib import Path
import requests
import time
from typing import List

# 3rd
from tqdm.auto import tqdm


class TangorinScraper(object):
    def __init__(self, out_dir="scrape/raw"):
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
