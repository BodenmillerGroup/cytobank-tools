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

import requests

logging.basicConfig()
log = logging.getLogger()
log.propagate = True

# CONFIGURATION

CYTOBANK = 'premium'
SOURCE_API = f'https://{CYTOBANK}.cytobank.org/cytobank/api/v1'


def authenticate(username: str, password: str):
    global authToken
    r = requests.post(f'{SOURCE_API}/authenticate', data={'username': username, 'password': password}).json()
    authToken = r['user']['authToken']


def list_experiments():
    r = requests.get(f'{SOURCE_API}/experiments', headers={'Authorization': f'Bearer {authToken}'}).json()
    return r


def download_experiment_details(id: int, output_dir: str):
    r = requests.get(f'{SOURCE_API}/experiments/{id}', headers={'Authorization': f'Bearer {authToken}'}).text
    with open(os.path.join(output_dir, 'experiment_details.json'), 'w') as file:
        file.write(r)


def download_all_fcs_files(id: int, output_dir: str):
    r = requests.get(f'{SOURCE_API}/experiments/{id}/fcs_files/download_zip',
                     headers={'Authorization': f'Bearer {authToken}'}, allow_redirects=True)
    with open(os.path.join(output_dir, 'fcs.zip'), 'wb') as file:
        file.write(r.content)


def download_gating_ml(id: int, output_dir: str):
    r = requests.get(f'{SOURCE_API}/experiments/{id}/download_gatingml',
                     headers={'Authorization': f'Bearer {authToken}'}, allow_redirects=True)
    with open(os.path.join(output_dir, 'gates.xml'), 'wb') as file:
        file.write(r.content)


def download_sample_tags(id: int, output_dir: str):
    r = requests.get(f'{SOURCE_API}/experiments/{id}/download_sample_tags',
                     headers={'Authorization': f'Bearer {authToken}'}, allow_redirects=True)
    with open(os.path.join(output_dir, 'sample_tags.tsv'), 'wb') as file:
        file.write(r.content)


def download_spade_analyses(id: int, output_dir: str):
    r = requests.get(f'{SOURCE_API}/experiments/{id}/advanced_analyses/spade',
                     headers={'Authorization': f'Bearer {authToken}'}).json()

    if len(r['spade']) > 0:
        sub_dir = os.path.join(output_dir, 'spades')
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
        for analysis in r['spade']:
            analysis_id = analysis['id']
            r = requests.get(
                f'{SOURCE_API}/experiments/{id}/advanced_analyses/spade/{analysis_id}/download?item=full_data',
                headers={'Authorization': f'Bearer {authToken}'}, allow_redirects=True)
            with open(os.path.join(sub_dir, f'{analysis_id}.zip'), 'wb') as file:
                file.write(r.content)


def download_all_attachments(id: int, output_dir: str):
    r = requests.get(f'{SOURCE_API}/experiments/{id}/attachments/download_zip',
                     headers={'Authorization': f'Bearer {authToken}'}, allow_redirects=True)
    with open(os.path.join(output_dir, 'attachments.zip'), 'wb') as file:
        file.write(r.content)


def export_experiment(id: int, output_dir: str):
    experiment_dir = os.path.join(output_dir, 'experiments', str(id))
    print(f'Processing experiment {id}... Output: {experiment_dir}')
    if not os.path.exists(experiment_dir):
        os.makedirs(experiment_dir)
    download_experiment_details(id, experiment_dir)
    download_all_fcs_files(id, experiment_dir)
    download_gating_ml(id, experiment_dir)
    download_sample_tags(id, experiment_dir)
    download_all_attachments(id, experiment_dir)
    download_spade_analyses(id, experiment_dir)


def main():
    parser = argparse.ArgumentParser(description='Import/export operations with Cytobank data.')
    parser.add_argument('-u', '--username', help='Username', type=str)
    parser.add_argument('-p', '--password', help='Password', type=str)
    parser.add_argument('-o', '--output', help='Output directory', type=str)

    args = parser.parse_args()
    print(args)

    if args.username is not None and args.password is not None and args.output is not None:
        authenticate(args.username, args.password)
        experiments = list_experiments()['experiments']

        for exp in experiments:
            experiment_id = exp['id']
            export_experiment(experiment_id, args.output)

        print("Done.")


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
