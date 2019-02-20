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
import os

from cytobank.Downloader import Downloader
from cytobank.Uploader import Uploader
from cytobank.Verify import Verify

logging.basicConfig()
log = logging.getLogger()
log.propagate = True


def main():
    parser = argparse.ArgumentParser(description='Import/export operations with Cytobank data.')
    parser.add_argument('command', help='Desired action: download or upload or verify', type=str)
    parser.add_argument('-u', '--username', help='Username', type=str)
    parser.add_argument('-p', '--password', help='Password', type=str)
    parser.add_argument('-b', '--bank', help='Cytobank name', type=str)
    parser.add_argument('-d', '--data', help='Data directory', type=str)
    parser.add_argument('-j', '--json', default=None, dest='local_json',
                        help='Use local json experiment fike. ' \
                        '(default:  %(default)s.)')

    args = parser.parse_args()
    print(args)

    if args.local_json:
        assert os.path.isfile(args.local_json), "Json file {0} not found.".format(args.local_json)

    if args.command is not None and args.username is not None and args.password is not None and args.bank is not None and args.data is not None:
        if args.command.lower() == 'download':
            downloader = Downloader(args.bank, args.data, args.username, args.password, json=args.local_json)
            downloader.download_all_experiments()
        elif args.command.lower() == 'upload':
            uploader = Uploader(args.bank, args.data, args.username, args.password)
            uploader.upload_all_experiments()
        elif args.command.lower() == 'verify':
            assert os.path.isfile(os.path.join(args.data,
                                               "experiments.json")), "Experiment json file 'experiments.json' not found in {0}.".format(args.data)
            verify = Verify(args.data, os.path.join(args.data,"experiments.json"))
            print("Found {0} missing experiments. ".format(verify.missing_experiments))
            if verify.missing_experiments:
                print("\nUse: `cytobank download -j {0}` to download missing " \
                      "experiments.".format(verify.missing_exp_file))
            
        else:
            raise Exception("Unknown command. Should be 'download' or 'upload'.")

        print("Done.")


if __name__ == '__main__':
    sys.exit(main())
