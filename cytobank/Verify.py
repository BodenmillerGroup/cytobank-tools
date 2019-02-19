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
EXP_FILENAME = "experiment_details.json"
TIMEOUT_PATTERN = "Authentication Timeout"


class Verify(Object):
    def __init__(self, data_dir: str, json: str):
        self.data_dir = data_dir
        self.json = json
        self.missing_json = os.path.join(self.data_dir, "experiments_missing.json")

        self.missing_experiments = self._search_timeout()
        if self.missing_experiments:
            self.json_missing = self._build_new_json(self.missing_experiments)

        self.missing_experiments_count = len(self.json_missing['experiments'])

        if len(self.json_missing['experiments']) > 0:
            json.dump(self.json_missing, self.missing_json)
        
    @property
    def missing_experiments(self):
        return self.missing_experiments_count
        
    def _search_timeout(self):
        missing = []

        for r,d,f in os.walk(self.data_dir):
            if EXP_FILENAME in f:
                with open(os.path.join(r,EXP_FILENAME),'r') as fd:
                    if TIMEOUT_PATTERN in fd.readlines():
                        # extract experiment ID for later
                        exp_id = os.path.basename(r)
                        print("Found missing experiment '{0}'".format(exp_id))
                        missing.append(int(exp_id))
        return missing

    def _build_new_json(self, missing_list):
        new_json = {'experiments': []}
        with open(self.json,'r') as fd:
            json_data = json.load(fd)

        for exp in json_data['experiments']:
            if exp['id'] in missing_list:
                new_json['experiments'].append(exp)

        return new_json
