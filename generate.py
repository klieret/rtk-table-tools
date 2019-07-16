#!/usr/bin/env python3

# std
import argparse

# ours
from rtktools.kanjicollection import KanjiCollection
from rtktools.scraper.tangorin.parser import TangorinParser
from rtktools.scraper.tangorin.scraper import TangorinScraper
from rtktools.poster import KanjiPoster


def usage(args):
    print("Use --help to show usage!")


def poster(args):
    k = KanjiCollection("data/kanjis.csv")
    p = KanjiPoster(k)
    with open("build/table.tex", "w") as outfile:
        outfile.write(p.generate())


def scrape(args):
    k = KanjiCollection("data/kanjis.csv")
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
