"""Helper functions for job submission

Author: Matthias van den Belt
"""
import os
import random
import typing as t

import werkzeug.datastructures
import werkzeug.utils

from flask import request

from cagecat import q, db
from cagecat.classes import CAGECATJob
from cagecat.general_utils import fetch_job_from_db
from cagecat.const import jobs_dir, folders_to_create
from cagecat.db_models import Job as dbJob


def prepare_search(job_id: str, job_type: str) -> t.Tuple[str, str]:
    """Parses input type for search module

    Input:
        - job_id: ID corresponding to the job the properties are asked for
        - job_type: type of job (e.g. search, recomputation or extraction)

    Output:
        - file_path: appropriate file path to be used in the next steps
        - job_type: type of job (e.g. search, recomputation or extraction)
            is changed when the the user asked for a recomputation
    """
    # save the files
    if 'inputType' in request.form:
        input_type = request.form["inputType"]

        if input_type == 'file':
            file_path = save_file(request.files["genomeFiles"], job_id)
        elif input_type == "ncbi_entries":
            file_path = None
        elif input_type == "prev_session":
            job_type = "recompute"
            file_path = get_previous_job_properties(job_id, job_type, "search")
        else:
            raise NotImplementedError(
                f"Input type {input_type} has not been implemented yet")
    else:
        file_path, job_type = None, 'search'

    return file_path, job_type


def get_previous_job_properties(job_id: str, job_type: str,
                                module: str) -> str:
    """Returns appropriate file path of previous job

    Input:
        - job_id: ID corresponding to the job the properties are asked for
        - job_type: type of job (e.g. search, recomputation or extraction)
        - module: name of module for which the properties are asked for

    Output:
        - file_path: appropriate file path to be used in the next steps
    """
    prev_job_id = request.form[f"{module}EnteredJobId"]
    check_valid_job(prev_job_id)

    file_path = os.path.join(jobs_dir, prev_job_id, "results",
                             f"{prev_job_id}_session.json")

    return file_path


def enqueue_jobs(new_jobs: t.List[CAGECATJob]) -> str:
    """Enqueues jobs on the Redis queue

    Input:
        - new_jobs: list of CAGECAT jobs that should be enqueued

    Output:
        - last_job_id: job ID of the last added job. Used to show appropriate
            results page and fetch a job which this job depends on, if
            applicable
    """
    if len(new_jobs) == 0:
        raise IOError("Submitted a job, but no job added to the list")

    created_redis_jobs_ids = []

    for i, cc_job in enumerate(new_jobs):  # cc_job = cagecat_job (CAGECATJob)
        create_directories(cc_job.job_id)
        save_settings(cc_job.options, cc_job.job_id)

        depending_on = None if cc_job.depends_on_job_id is None else \
            created_redis_jobs_ids[i-1][1]

        job = q.enqueue(cc_job.function,
                        args=(cc_job.job_id, ),
                        kwargs={'options': cc_job.options,
                                'file_path': cc_job.file_path},
                        depends_on=depending_on,
                        result_ttl=86400)

        main_search_job_id = add_parent_search_and_child_jobs_to_db(cc_job, i == len(new_jobs)-1)

        j = dbJob(id=cc_job.job_id,
                  status="queued" if depending_on is None else "waiting",  # for parent job to finish
                  job_type=cc_job.job_type,
                  redis_id=job.id,
                  depending_on='null' if depending_on is None else cc_job.depends_on_job_id,
                  main_search_job=main_search_job_id,
                  title=cc_job.title,
                  email=cc_job.email)

        db.session.add(j)
        db.session.commit()

        created_redis_jobs_ids.append((cc_job.job_id, job.id))
        last_job_id = cc_job.job_id

    return last_job_id


def add_parent_search_and_child_jobs_to_db(new_job: CAGECATJob,
                                           is_last_job: bool) -> str:
    """Adds the main search job and its children to the new_job in db

    Input:
        - new_job: a CAGECAT job of which the connected jobs should be
            added to the SQL db
        - is_last_job: indicates if this is the last job being added to the
            queue (used in enqueue_jobs())

    Output:
        - job id of the main search job
    """
    if new_job.get_job_type() == 'search':
        main_search_job_id = "null"
    else:
        old_job = get_parent_job(new_job, is_last_job)

        if old_job == 'null':
            main_search_job_id = 'null'
        elif old_job.job_type == "search":
            main_search_job_id = old_job.id
            main_search_job = fetch_job_from_db(main_search_job_id)

            sep = "" if not main_search_job.child_jobs else ","
            main_search_job.child_jobs += f"{sep}{new_job.job_id}"
            # empty string for the first child job
        else:
            main_search_job_id = old_job.main_search_job

    return main_search_job_id


def get_parent_job(new_job: CAGECATJob,
                   is_last_job: bool) -> t.Union[str, dbJob, None]:
    """Gets the parent job of a job (i.e. the job this job depends on)

    Input:
        - new_job: a CAGECAT job of which the parent job should be fetched
        - is_last_job: indicates if this is the last job being added to the
            queue (used in enqueue_jobs())

    Output:
        - parent Job instance
    """
    j_type = new_job.get_job_type()
    if j_type in ("recompute", "gne", "clinker"):
        # are modules which use the prev_session macro to get the previous session ID
        # might change in the future

        # below lines are required due to the naming in the HTML input fields
        if j_type == "recompute":
            module = "search"
        elif j_type == "clinker":
            module = "clinker"

            if f"{module}EnteredJobId" not in new_job.options:
                return 'null'
        else:
            module = j_type

        key = f"{module}EnteredJobId"
    else:
        key = "prev_job_id"

    return fetch_job_from_db(
        new_job.options[key] if is_last_job else new_job.file_path.split(os.sep)[2])


def validate_full_form(form_type, request_form):
    standard_attributes = ('Meta', 'meta', 'form_errors', 'errors', 'data', 'populate_obj', 'process', 'validate')
    large_form = form_type(request_form)
    all_valid = True

    all_forms = [attr for attr in dir(large_form) if not attr.startswith('_') and attr not in standard_attributes]

    for form in all_forms:
        smaller_form = large_form.__getattribute__(form)
        smaller_form.process(request_form)

        is_valid = smaller_form.validate()
        print(smaller_form, smaller_form.errors)

        if not is_valid:
            all_valid = False

    return all_valid


def generate_job_id(id_len: int = 15) -> str:
    """Generates a numeric job ID with each 4th character being a letter

    Input:
        - id_len, int: length of the job ID to be generated

    Output:
        - job_id, str: a randomly generated job ID
    """
    characters = []
    existing_job = 0

    while existing_job is not None:
        for i in range(id_len):
            if i % 4 == 0:
                min_ord, max_ord = 65, 90
            else:
                min_ord, max_ord = 48, 57

            characters.append(chr(random.randint(min_ord, max_ord)))

        job_id = "".join(characters)
        existing_job = fetch_job_from_db(job_id)
        # existing_job becomes None if no such job exists

    return job_id


def save_file(file_obj: werkzeug.datastructures.FileStorage,
              job_id: str) -> str:
    """Saves file in specific job uploads folder using the provided filename

    Input:
        - file_obj: via HTTP form user submitted file. Given like:
            request.form[filename]
        - job_id, str: ID corresponding to the job the function is called for

    Output:
        - file_path, str: path where the file has been saved
    """
    fn = werkzeug.utils.secure_filename(file_obj.filename)
    if fn:

        file_path = os.path.join(f"{jobs_dir}", job_id,
                                 "uploads", fn)
        file_obj.save(file_path)
    else:
        raise IOError('Securing filename led to an empty filename')

    return file_path


def create_directories(job_id: str) -> None:
    """Creates directories for a job ID

    Input:
        - job_id: ID corresponding to the job the function is called for

    Output:
        - None
        - Created directories
    """
    base_path = os.path.join(jobs_dir, job_id)

    if not os.path.exists(base_path): # directories are attempted to
        # be created again when jobs depending on each other are executed
        os.mkdir(base_path)
        for folder in folders_to_create:
            os.mkdir(os.path.join(base_path, folder))


def save_settings(options: werkzeug.datastructures.ImmutableMultiDict,
                  job_id: str) -> None:
    """Writes job settings to a file with which the job was submitted

    Input:
        - options: user submitted options (values) via HTTP form of front-end
        - job_id: ID corresponding to the job the function is called for

    Output:
        - None
        - New file with options written to it

    Function created for logging purposes. Writes to a file, which will be
    used by the [load_settings] function.
    """
    with open(f"{os.path.join(jobs_dir, job_id, 'logs', job_id)}"
              f"_options.txt", "w") as outf:

        for key, value in options.items():
            if type(value) == str:
                if "\r\n" in value:
                    value = ','.join(value.split('\r\n'))

            outf.write(f"{key},{value}\n")


def check_valid_job(prev_job_id: str) -> None:
    """Checks if a submitted job, relying on a previous job is valid

    Input:
        - prev_job_id: ID of the user-submitted previous job

    Output:
        - None

    Raises:
        - NotImplementedError: when previous_job_id was not found in
            the database
    """
    if fetch_job_from_db(prev_job_id) is None:
        raise NotImplementedError("Unknown job ID. Template should be created")
