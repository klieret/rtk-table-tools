#!/usr/bin/env python3

# std
import argparse
from pathlib import Path, PurePath
from typing import Union
from subprocess import Popen
import os

# ours
from rtktools.kanjicollection import KanjiCollection
from rtktools.scraper.tangorin.parser import TangorinParser
from rtktools.scraper.tangorin.scraper import TangorinScraper
from rtktools.poster import get_available_poster_styles, poster_by_name
from rtktools.util.log import log


THIS_DIR = Path(__file__).parent


def get_kanji_collection():
    tangorin_path = None
    tangorin_path_conjecture = THIS_DIR / "scrape" / "tangorin.csv"
    if Path(tangorin_path_conjecture).is_file():
        tangorin_path = tangorin_path_conjecture
    kc = KanjiCollection(
        path=THIS_DIR / "data" / "kanjis.csv",
        tangorin_path=tangorin_path
    )
    log.info("Loaded Kanji collection with {} kanji.".format(len(kc)))
    return kc

def usage(args):
    print("Use --help to show usage!")


def latex_render_table(path: Union[str, PurePath]) -> None:
    path = Path(path)
    log.info("Rendering using XeLaTeX. Output files and "
             "logs are in directory {}.".format(path.parent))
    Popen(
        [
            "xelatex",
            "--output-directory={}".format(path.parent),
            "-interaction=nonstopmode",
            str(path)
        ],
        stdout=open(os.devnull, 'w')
    ).communicate()


def poster(args):
    k = get_kanji_collection()
    p = poster_by_name(args.style, k)
    outpath = THIS_DIR / "build" / "table.tex"
    p.generate(path=outpath)
    log.info("Finished generating poster code.")
    if not args.no_render:
        latex_render_table(outpath)


def scrape(args):
    k = get_kanji_collection()
    ts = TangorinScraper()
    ts.download_kanjis(k.kanjis)


def parse(args):
    tp = TangorinParser()
    tp.save2csv(tp.parse_dir(THIS_DIR / "scrape" / "raw/"))


def cli():
    parser = argparse.ArgumentParser(description="RTK Tools")
    subparsers = parser.add_subparsers(
        title="Subcommands"
    )
    parser.set_defaults(func=usage)

    # Poster CLI
    # --------------------------------------------------------------------------
    poster_parser = subparsers.add_parser("poster")
    poster_parser.add_argument(
        "--no-render",
        action="store_true",
        default=False,
        help="Skip XeLaTeX rendering."
    )
    poster_parser.add_argument(
        "--style", "-s",
        default="default",
        help="Poster style",
        choices=get_available_poster_styles()
    )
    poster_parser.set_defaults(func=poster)

    # Scraper CLI
    # --------------------------------------------------------------------------
    scrape_parser = subparsers.add_parser("scrape")
    scrape_parser.set_defaults(func=scrape)

    # Parser CLI
    # --------------------------------------------------------------------------
    parser_parser = subparsers.add_parser("parse")
    parser_parser.set_defaults(func=parse)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    cli()
