"""Module to create HMMer databases

This script should be ran parallel to the construct_hmm_databases.sh
script, as this script waits for a file, indicating a genus, created by that
script that a database is ready to be created

Author: Matthias van den Belt
"""
import subprocess
import time
import os
import sys
import typing as t
import shutil
import requests

sys.path.append('..')
from config_files.sensitive import finished_hmm_db_folder, hmm_db_genome_downloads
from config_files.config import hmm_db_creation_conf

def list_files(_genus: str) -> t.List[str]:
    """Lists all present GenBank files for the given genus

    Input:
        - genus: name of genus to list files for

    Output:
        - list of file paths belonging to the given genus
    """
    all_files = []

    for root, directory, files in os.walk(os.path.join(hmm_db_genome_downloads, organism, _genus)):
        for f in files:
            all_files.append(os.path.join(root, f))

    return all_files


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print('Enter if existing databases should be removed')
    #     exit(0)
    if len(sys.argv) == 1:
        raise IndexError('No organism supplied')

    organism = sys.argv[1]
    if organism not in ('prokaryota', 'fungi'):
        raise ValueError('Invalid organism')

    if len(sys.argv) == 3:
        remove_dbs = sys.argv[2]
    else:
        remove_dbs = input('Remove old databases? (y/n) ')

    if remove_dbs == 'y':
        print('Removing databases', flush=True)

        os.chdir(finished_hmm_db_folder)
        for f in os.listdir():
            try:
                os.remove(f)
            except IsADirectoryError:
                shutil.rmtree(f)

            print(f'  Removed: {f}', flush=True)  # remove old db's
    elif remove_dbs == 'n':
        pass
    else:
        raise ValueError('Invalid option entered')

    folders_to_create = [
        os.path.join(finished_hmm_db_folder, 'logs', organism),
        os.path.join(finished_hmm_db_folder, organism)
    ]

    for path in folders_to_create:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    while True:
        try:
            dbs_to_create_path = os.path.join(hmm_db_genome_downloads, organism, 'databases_to_create')
            dbs_to_create = os.listdir(dbs_to_create_path)
        except FileNotFoundError:
            print('No databases_to_create folder present yet')
            print(f'Sleeping for {hmm_db_creation_conf["sleeping_time"]} seconds', flush=True)
            time.sleep(hmm_db_creation_conf['sleeping_time'])
            continue

        if len(dbs_to_create) == 0:
            print(f'Nothing to create. Sleeping for {hmm_db_creation_conf["sleeping_time"]} seconds', flush=True)
            time.sleep(hmm_db_creation_conf['sleeping_time'])
        elif len(dbs_to_create) == 1 and dbs_to_create[0] == 'stop_creating_databases':
            print('Encountered the stop_creating_databases file', flush=True)
            subprocess.run(['rm', os.path.join(dbs_to_create_path, 'stop_creating_databases')])
            print('Finished creating all databases.', flush=True)

            res = requests.get('https://www.bioinformatics.nl/cagecat/update-hmm-databases')

            if res.text == '1':
                print('Successfully updated the available databases variable in the back-end, which is used to create the front-end')
            else:
                print('Something did not go well when updating the available databases')

            exit(0)
        else:
            for genus in dbs_to_create:
                if genus == 'stop_creating_databases':
                    continue  # as we don't want to make a db for this file
                    # actually create the db
                print(f'Creating {genus} database', flush=True)
                cmd = ["cblaster", "makedb",
                       "--name", os.path.join(finished_hmm_db_folder, organism, genus),
                       "--cpus", hmm_db_creation_conf['cpus'],
                       "--batch", hmm_db_creation_conf['batch_size']]

                cmd.extend(list_files(genus))

                if len(cmd) == 8: # indicates no files were added
                    print(f'{genus} has no genome files. Continuing..', flush=True)
                    continue

                with open(os.path.join(finished_hmm_db_folder, 'logs', organism, f'{genus}_creation.log'), 'w') as outf:
                    res = subprocess.run(cmd, stderr=outf, stdout=outf, text=True)

                if res.returncode != 0:
                    print('Something went wrong. Exiting..', flush=True)
                    exit(1)

                print(f'  Successfully created {genus} HMM database', flush=True)
                subprocess.run(['rm', os.path.join(dbs_to_create_path, genus)])
                print(f'  Removed {genus} touch file', flush=True)


# TODO future: we could compress all refseq gbks until the next time we use it so we save storage
# example command:
# tar cvf - $fp --remove-files | gzip -9 - > $fp.tar.gz
