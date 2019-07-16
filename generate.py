#!/usr/bin/env python3

# std
import argparse
from pathlib import Path, PurePath
from typing import Union
from subprocess import Popen

# ours
from rtktools.kanjicollection import KanjiCollection
from rtktools.scraper.tangorin.parser import TangorinParser
from rtktools.scraper.tangorin.scraper import TangorinScraper
from rtktools.poster import KanjiPoster


# todo: remove absolute paths!
def get_kanji_collection():
    tangorin_path = None
    tangorin_path_conjecture = "scrape/tangorin.csv"
    if Path(tangorin_path_conjecture).is_file():
        tangorin_path = tangorin_path_conjecture
    return KanjiCollection(
        path="data/kanjis.csv",
        tangorin_path=tangorin_path
    )


def usage(args):
    print("Use --help to show usage!")


def latex_render_table(path: Union[str, PurePath]) -> None:
    path = str(path)
    Popen(["xelatex", "--output-directory=build", path]).communicate()


def poster(args):
    k = get_kanji_collection()
    p = KanjiPoster(k)
    outpath = "build/table.tex"
    p.generate(path=outpath)
    latex_render_table("main.tex")


def scrape(args):
    k = get_kanji_collection()
    ts = TangorinScraper()
    ts.download_kanjis(k.kanjis)


def parse(args):
    tp = TangorinParser()
    tp.save2csv(tp.parse_dir("scrape/raw/"))


def cli():
    parser = argparse.ArgumentParser(description="RTK Tools")
    subparsers = parser.add_subparsers(
        title="Subcommands"
    )
    parser.set_defaults(func=usage)
    poster_parser = subparsers.add_parser("poster")
    poster_parser.set_defaults(func=poster)
    scrape_parser = subparsers.add_parser("scrape")
    scrape_parser.set_defaults(func=scrape)
    parser_parser = subparsers.add_parser("parse")
    parser_parser.set_defaults(func=parse)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    cli()
