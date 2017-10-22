#!/usr/bin/env python3

import argparse
from killtheshapefile import prepare_data
from killtheshapefile import make_stats
import logging
import killtheshapefile
import os


def main():
    logger = logging.getLogger("killtheshapefile")
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--tempdir", required=False, help="temporary directory", type=str)
    parser.add_argument("--output", default="./outputs/", help="output directory", type=str)
    parser.add_argument("--input", required=False, help="input zipped shapefile", type=argparse.FileType("r"))
    parser.add_argument("--where", required=False, help="-where config for ogrinfo", type=str)
    parser.add_argument("--fid", required=False, help="-fid config for ogrinfo", type=int)
    parser.add_argument("--spat", required=False, metavar="coord",
            help="-spat config for ogrinfo", type=float, nargs=4)
    parser.add_argument("--repeat", required=False, metavar="NUMBER",
            help="Repeat time measure X times", type=int, default=1)
    args = parser.parse_args()

    if args.output == "./outputs/":
        output = os.path.abspath(os.path.join(
                os.path.split(killtheshapefile.__file__)[0],
                args.output
        ))
    else:
        output = args.output

    if not os.path.isdir(output):
        os.mkdir(output)

    formats = prepare_data(args.tempdir, args.input.name)
    stats = make_stats(formats, output, args.repeat, args.where, args.fid, args.spat)

if __name__ == "__main__":
    main()
