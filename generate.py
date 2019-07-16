#!/usr/bin/env python3

# ours
from rtktools.kanjicollection import KanjiCollection
from rtktools.scraper.tangorin.parser import TangorinParser
from rtktools.scraper.tangorin.scraper import TangorinScraper
from rtktools.poster import KanjiPoster


if __name__ == "__main__":
    k = KanjiCollection("data/kanjis.csv")
    # kp = KanjiPoster(k)
    # ts = TangorinScraper()
    # ts.download_kanjis(k.kanjis)
    tp = TangorinParser()
    tp.save2csv(tp.parse_dir("scrape/raw/"))
    # lt.ncols = 10
    # with open("build/table.tex", "w") as outfile:
    #     outfile.write(lt.generate())
