"""Module to remove stored data of jobs that have ran > 30 days ago.

Author: Matthias van den Belt
"""

import os
import datetime
import shutil
import typing as t

from config_files.sensitive import maintenance_logs, server_prefix
from cagecat import db
from cagecat.general_utils import fetch_job_from_db
from cagecat.const import jobs_dir
from config_files.config import persistent_jobs


def get_folders_to_delete(period_to_keep: int = 31) -> t.List[t.Tuple[str, str]]:
    """Returns the folders which are too old to keep (and should be deleted)

    Input:
        - period_to_keep: how many days files should be stored on the server

    Output:
        - to_delete: directory path and job ID's to delete
    """

    to_delete = []
    current = datetime.datetime.now()
    j_dir = os.path.join(server_prefix, jobs_dir)

    for fn in os.listdir(j_dir):
        fp = os.path.join(j_dir, fn)
        if os.path.isdir(fp):
            if (current - datetime.datetime.fromtimestamp(os.path.getmtime(fp))).days >= period_to_keep:
                to_delete.append((fp, os.path.split(fp)[-1]))

    return to_delete


def delete_old_jobs():
    """Delete old jobs from the server

    Output:
        - None, entries are removed from the database and job folders which
            have expired the storage data are removed
    """
    with open(os.path.join(f'{maintenance_logs}',
                           f'{datetime.datetime.now().date()}_removal.txt'),
              'w') as outf:
        for directory, job_id in get_folders_to_delete():

            if job_id in persistent_jobs:
                print(f'Skipped: {job_id} (in persistent jobs)')
                continue
            try:
                shutil.rmtree(directory)
            except FileNotFoundError:  # occurred during development.
                #  will not happen in production
                print(f'Directory not found: {directory}')

            db.session.delete(fetch_job_from_db(job_id))

            outf.write(f'Deleted: {directory}\n')

        outf.write('Finished deleting jobs')

    db.session.commit()


if __name__ == '__main__':
    delete_old_jobs()
