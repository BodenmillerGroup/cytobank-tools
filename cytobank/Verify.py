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

import os
import json

EXP_FILENAME = "experiment_details.json"
TIMEOUT_PATTERN = "Authentication Timeout"


class Verify():
    def __init__(self, data_dir: str, exp_json: str):
        self.data_dir = data_dir
        self.exp_json = exp_json
        self.missing_exp_file = os.path.join(self.data_dir, "experiments_missing.json")

        self.downloaded_experiments = [int(os.path.basename(exp)) for exp in os.listdir(self.data_dir) if os.path.isdir(os.path.join(self.data_dir,
                                                                                                                                exp))]
        self.all_experiments = self._get_all_experiments()

        self.missing_exp_list = []
        self.missing_exp_list.extend(self._search_timeout())
        self.missing_exp_list.extend(self._get_non_downloaded_experiments())

        self.missing_exp_json = self._build_new_json(self.missing_exp_list)

        if len(self.missing_exp_json['experiments']) > 0:
            with open(self.missing_exp_file, 'w+') as fd:
                json.dump(self.missing_exp_json, fd)
        
    @property
    def missing_experiments(self):
        return len(self.missing_exp_json['experiments'])

    def _get_non_downloaded_experiments(self):
        # Compare list of downloaded with lost of all
        return list(set(self.all_experiments) - set(self.downloaded_experiments))

    def _get_all_experiments(self):
        experiments = []
        with open(self.exp_json,'r') as fd:
            json_data = json.load(fd)
            for exp in json_data['experiments']:
                experiments.append(exp['id'])
        return experiments

    def _search_timeout(self):
        missing = []

        for r,d,f in os.walk(self.data_dir):
            if EXP_FILENAME in f:
                with open(os.path.join(r,EXP_FILENAME),'r') as fd:
                    if TIMEOUT_PATTERN in fd.read():
                        # extract experiment ID for later
                        exp_id = os.path.basename(r)
                        missing.append(int(exp_id))
        return missing

    def _build_new_json(self, missing_list):
        new_json = {'experiments': []}
        with open(self.exp_json,'r') as fd:
            json_data = json.load(fd)

        for exp in json_data['experiments']:
            if exp['id'] in missing_list:
                new_json['experiments'].append(exp)

        return new_json
