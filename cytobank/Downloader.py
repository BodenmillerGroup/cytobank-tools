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

import requests

from cytobank.ApiBase import ApiBase


class Downloader(ApiBase):
    def __init__(self, bank: str, data_dir: str, username: str, password: str, json = None):
        super().__init__(bank)
        self.data_dir = data_dir
        self.json = json
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.authenticate(username, password)

    def list_experiments(self):
        # Use local json if defined
        # Get full experiment json otherwise
        if self.json:
            json_data = None
            with open(self.json, 'r') as fd:
                json_data = json.load(fd)
            return json_data
        else:
            r = requests.get(f'{self.api_url}/experiments', headers={'Authorization': f'Bearer {self.token}'}).json()
            with open(os.path.join(self.data_dir, 'experiments.json'), 'w') as file:
                json.dump(r, file)
            return r

    def download_experiment_details(self, id: int, experiment_dir: str):
        r = requests.get(f'{self.api_url}/experiments/{id}', headers={'Authorization': f'Bearer {self.token}'}).json()
        with open(os.path.join(experiment_dir, 'experiment_details.json'), 'w') as file:
            json.dump(r, file)

    def download_all_fcs_files_as_zip(self, id: int, experiment_dir: str):
        r = requests.get(f'{self.api_url}/experiments/{id}/fcs_files/download_zip',
                         headers={'Authorization': f'Bearer {self.token}'})
        with open(os.path.join(experiment_dir, 'fcs.zip'), 'wb') as file:
            file.write(r.content)

    def download_all_fcs_files(self, id: int, experiment_dir: str):
        r = requests.get(f'{self.api_url}/experiments/{id}/fcs_files',
                         headers={'Authorization': f'Bearer {self.token}'}).json()

        with open(os.path.join(experiment_dir, 'fcs.json'), 'w') as file:
            json.dump(r, file)

        if 'fcsFiles' in r and len(r['fcsFiles']) > 0:
            sub_dir = os.path.join(experiment_dir, 'fcs')
            if not os.path.exists(sub_dir):
                os.makedirs(sub_dir)
            for fcs_file in r['fcsFiles']:
                fcs_file_id = fcs_file['id']
                fcs_filename = fcs_file['filename']
                r = requests.get(
                    f'{self.api_url}/experiments/{id}/fcs_files/{fcs_file_id}/download',
                    headers={'Authorization': f'Bearer {self.token}'})
                with open(os.path.join(sub_dir, f'{fcs_filename}'), 'wb') as file:
                    file.write(r.content)

    def download_gating_ml(self, id: int, experiment_dir: str):
        r = requests.get(f'{self.api_url}/experiments/{id}/download_gatingml',
                         headers={'Authorization': f'Bearer {self.token}'})
        with open(os.path.join(experiment_dir, 'gates.xml'), 'wb') as file:
            file.write(r.content)

    def download_sample_tags(self, id: int, experiment_dir: str):
        r = requests.get(f'{self.api_url}/experiments/{id}/download_sample_tags',
                         headers={'Authorization': f'Bearer {self.token}'})
        with open(os.path.join(experiment_dir, 'sample_tags.tsv'), 'wb') as file:
            file.write(r.content)

    def download_spade_analyses(self, id: int, experiment_dir: str):
        r = requests.get(f'{self.api_url}/experiments/{id}/advanced_analyses/spade',
                         headers={'Authorization': f'Bearer {self.token}'}).json()

        if 'spade' in r and len(r['spade']) > 0:
            sub_dir = os.path.join(experiment_dir, 'spades')
            if not os.path.exists(sub_dir):
                os.makedirs(sub_dir)
            for analysis in r['spade']:
                analysis_id = analysis['id']
                r = requests.get(
                    f'{self.api_url}/experiments/{id}/advanced_analyses/spade/{analysis_id}/download?item=full_data',
                    headers={'Authorization': f'Bearer {self.token}'})
                with open(os.path.join(sub_dir, f'{analysis_id}.zip'), 'wb') as file:
                    file.write(r.content)

    def download_all_attachments_as_zip(self, id: int, experiment_dir: str):
        r = requests.get(f'{self.api_url}/experiments/{id}/attachments/download_zip',
                         headers={'Authorization': f'Bearer {self.token}'})
        with open(os.path.join(experiment_dir, 'attachments.zip'), 'wb') as file:
            file.write(r.content)

    def download_all_attachments(self, id: int, experiment_dir: str):
        r = requests.get(f'{self.api_url}/experiments/{id}/attachments',
                         headers={'Authorization': f'Bearer {self.token}'}).json()

        with open(os.path.join(experiment_dir, 'attachments.json'), 'w') as file:
            json.dump(r, file)

        if 'attachments' in r and len(r['attachments']) > 0:
            sub_dir = os.path.join(experiment_dir, 'attachments')
            if not os.path.exists(sub_dir):
                os.makedirs(sub_dir)
            for attachment_file in r['attachments']:
                attachment_file_id = attachment_file['id']
                attachment_filename = attachment_file['filename']
                r = requests.get(
                    f'{self.api_url}/experiments/{id}/attachments/{attachment_file_id}/download',
                    headers={'Authorization': f'Bearer {self.token}'})
                with open(os.path.join(sub_dir, f'{attachment_filename}'), 'wb') as file:
                    file.write(r.content)

    def export_experiment(self, id: int):
        experiment_dir = os.path.join(self.data_dir, str(id))
        print(f'Processing experiment {id}... Output: {experiment_dir}')
        if not os.path.exists(experiment_dir):
            os.makedirs(experiment_dir)
        self.download_experiment_details(id, experiment_dir)
        self.download_all_fcs_files(id, experiment_dir)
        # self.download_all_fcs_files_as_zip(id, experiment_dir)
        self.download_gating_ml(id, experiment_dir)
        self.download_sample_tags(id, experiment_dir)
        self.download_all_attachments(id, experiment_dir)
        # self.download_spade_analyses(id, experiment_dir)

    def download_all_experiments(self):
        experiments = self.list_experiments()['experiments']

        for exp in experiments:
            if not exp['public']:
                experiment_id = exp['id']
                self.export_experiment(experiment_id)
