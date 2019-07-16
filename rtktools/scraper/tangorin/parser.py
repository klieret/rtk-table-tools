#!/usr/bin/env python3

# std
from pathlib import PurePath, Path
import json
import collections

# 3rd
from bs4 import BeautifulSoup
from tqdm.auto import tqdm


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

    def save2csv(self, dct, path="scrape/tangorin.csv"):
        path = Path(path)
        df = pd.DataFrame(dct)
        df.to_csv(path)
