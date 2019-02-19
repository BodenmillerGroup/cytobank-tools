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

import json
import os

import requests

from cytobank.ApiBase import ApiBase


class Uploader(ApiBase):
    def __init__(self, bank: str, data_dir: str, username: str, password: str):
        super().__init__(bank, username, password)
        self.data_dir = data_dir
        self.authenticate()

    def load_experiments(self):
        with open(os.path.join(self.data_dir, 'experiments.json'), 'r') as file:
            return json.load(file)

    def load_experiment_details(self, experiment_dir: str):
        with open(os.path.join(experiment_dir, 'experiment_details.json'), 'r') as file:
            return json.load(file)

    def load_fcs_details(self, experiment_dir: str):
        with open(os.path.join(experiment_dir, 'fcs.json'), 'r') as file:
            return json.load(file)

    def load_attachments_details(self, experiment_dir: str):
        with open(os.path.join(experiment_dir, 'attachments.json'), 'r') as file:
            return json.load(file)

    def create_experiment(self, experiment_dir: str):
        expriment_details = self.load_experiment_details(experiment_dir)['experiment']
        payload = {
            "experiment":
                {
                    "experimentName": expriment_details['experimentName'],
                    "primaryResearcherId": self.user_id, # expriment_details['primaryResearcherId'],
                    "principalInvestigatorId": self.user_id, # expriment_details['principalInvestigatorId'],
                    "projectId": expriment_details['projectId'],
                    "purpose": expriment_details['purpose'],
                    "comments": expriment_details['comments']
                }
        }
        r = requests.post(f'{self.api_url}/experiments', headers={'Authorization': f'Bearer {self.token}'},
                          json=payload).json()
        return r

    # Uploading via zip files doesn't work properly due to API error. Issue was reported to Cytobank.
    def upload_all_fcs_files_as_zip(self, id: int, experiment_dir: str):
        with open(os.path.join(experiment_dir, 'fcs.zip'), 'rb') as file:
            files = {'file': file}
            r = requests.post(f'{self.api_url}/experiments/{id}/fcs_files/upload_zip',
                              headers={'Authorization': f'Bearer {self.token}'}, files=files)
            print(r.text)

    def upload_all_fcs_files(self, id: int, experiment_dir: str):
        fcs = self.load_fcs_details(experiment_dir)['fcsFiles']

        if len(fcs) > 0:
            for fcs_file in fcs:
                with open(os.path.join(experiment_dir, 'fcs', fcs_file['filename']), 'rb') as file:
                    files = {'file': file}
                    r = requests.post(f'{self.api_url}/experiments/{id}/fcs_files/upload',
                                      headers={'Authorization': f'Bearer {self.token}'}, files=files)
                    print(r.text)

    def upload_gating_ml(self, id: int, experiment_dir: str):
        with open(os.path.join(experiment_dir, 'gates.xml'), 'rb') as file:
            files = {'file': file}
            r = requests.post(f'{self.api_url}/experiments/{id}/upload_gatingml',
                             headers={'Authorization': f'Bearer {self.token}'}, files=files)
            print(r.text)

    def upload_sample_tags(self, id: int, experiment_dir: str):
        with open(os.path.join(experiment_dir, 'sample_tags.tsv'), 'rb') as file:
            files = {'file': file}
            r = requests.post(f'{self.api_url}/experiments/{id}/upload_sample_tags',
                             headers={'Authorization': f'Bearer {self.token}'}, files=files)
            print(r.text)

    def upload__all_attachments(self, id: int, experiment_dir: str):
        attachments = self.load_attachments_details(experiment_dir)['attachments']

        if len(attachments) > 0:
            for attachment_file in attachments:
                with open(os.path.join(experiment_dir, 'attachments', attachment_file['filename']), 'rb') as file:
                    files = {'file': file}
                    r = requests.post(f'{self.api_url}/experiments/{id}/attachments/upload',
                                      headers={'Authorization': f'Bearer {self.token}'}, files=files)
                    print(r.text)

    def upload_experiment(self, id: int):
        experiment_dir = os.path.join(self.data_dir, str(id))
        print(f'Processing experiment {id}...')
        if not os.path.exists(experiment_dir):
            raise Exception(f'Experiment folder {id} does not exist.')
        experiment = self.create_experiment(experiment_dir)['experiment']
        experiment_id = experiment['id']
        self.upload_all_fcs_files(experiment_id, experiment_dir)
        # self.upload_all_fcs_files_as_zip(experiment_id, experiment_dir)
        self.upload__all_attachments(experiment_id, experiment_dir)
        self.upload_sample_tags(experiment_id, experiment_dir)
        self.upload_gating_ml(experiment_id, experiment_dir)

    def upload_all_experiments(self):
        experiments = self.load_experiments()['experiments']

        for exp in experiments:
            if not exp['public']:
                experiment_id = exp['id']
                self.upload_experiment(experiment_id)
