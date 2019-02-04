#!/usr/bin/env python
#
#  Copyright (C) 2019 - bodenmillerlab, University of Zurich
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 2 of the License, or (at your
#  option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import argparse
import logging
import sys

from cytobank.Downloader import Downloader

logging.basicConfig()
log = logging.getLogger()
log.propagate = True


def main():
    parser = argparse.ArgumentParser(description='Import/export operations with Cytobank data.')
    parser.add_argument('-u', '--username', help='Username', type=str)
    parser.add_argument('-p', '--password', help='Password', type=str)
    parser.add_argument('-b', '--bank', help='Cytobank', type=str)
    parser.add_argument('-o', '--output', help='Output directory', type=str)

    args = parser.parse_args()
    print(args)

    if args.username is not None and args.password is not None and args.bank is not None and args.output is not None:
        downloader = Downloader(args.bank, args.output, args.username, args.password)
        downloader.download_all_experiments()

        print("Done.")


if __name__ == '__main__':
    sys.exit(main())
