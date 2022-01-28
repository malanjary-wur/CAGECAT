"""Module to store classes used in CAGECAT

Author: Matthias van den Belt
"""

import cagecat.workers.workers as w

function_dict = {'search': w.cblaster_search,
                 'recompute': w.cblaster_search,
                 'gne': w.cblaster_gne,
                 'extract_sequences': w.cblaster_extract_sequences,
                 'extract_clusters': w.cblaster_extract_clusters,
                 # 'corason': w.corason,
                 'clinker': w.clinker,
                 'clinker_query': w.clinker_query}

class CAGECATJob:
    """Class to temporarily store settings required to create a CAGECAT job

    Input:
        - job_id: CAGECAT generated job ID
        - options: dictionary of options submitted by the user via the HTML
            front-end
        - job_type: the type of job
        - file_path: file path used during execution of the worker function
            (i.e. refers to a session file of previous job)
        - depends_on_job_id: ID of the job on which the current job depends
            if so
    """

    def __init__(self, job_id, options,
                 job_type=None,
                 file_path=None,
                 depends_on_job_id=None):

        self.job_id = job_id
        self.options = options
        self.file_path = file_path
        self.depends_on_job_id = depends_on_job_id
        self.function = function_dict[self.options['job_type']] \
            if job_type is None else function_dict[job_type]

        self.title = options['job_title'] if 'job_title' in options else ''
        self.email = options['mail_address'] if 'mail_address' in options else ''
        self.job_type = job_type

        if self.job_type is None:
            self.job_type = self.options['job_type']

    def get_job_type(self):
        # TODO: check if this can be removed
        return self.options['job_type']
