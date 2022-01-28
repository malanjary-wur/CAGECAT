"""Stores routes for Flask web application for job result pages

Author: Matthias van den Belt
"""

# package imports
import copy
import json

from flask import Blueprint, request, url_for, send_file

# own project imports
from cagecat.routes.routes_helpers import format_size
from cagecat.const import execution_stages_front_end, execution_stages_log_descriptors, modules_with_plots, downstream_modules, \
    module_to_tool
from cagecat.general_utils import show_template, generate_paths, fetch_job_from_db
from cagecat.result.result_helpers import prepare_finished_result, get_connected_jobs, get_failure_reason


# other imports
import os

# typing imports
import flask.wrappers
import typing as t

result = Blueprint('result', __name__, template_folder="templates")

### Route function definitions
@result.route("/<job_id>")
def show_result(job_id: str, pj=None, store_job_id=False, j_type=None) -> str: # parent_job should be
    """Shows the results page for the given job ID

    Input:
        - job_id: job ID for a previously submitted job for which the user
            would like to view the results

    Output:
        - HTML represented in string format. Renders different templates based
            on the status of the given job ID

    Raises:
        - IOError: when for some reason a job's status is not valid. Currently
            valid options are: ["finished", "failed", "queued", "running"]

    Shows the "job_not_found.html" template when the given job ID was not
    found in the SQL database
    """
    job = fetch_job_from_db(job_id)

    if job is not None:
        status = job.status

        if status == "finished":
            module = job.job_type
            plot_contents, program, size = prepare_finished_result(
                job_id, module)
            # plot contents is not used currently. left in for future purposes
            #
            # with open(os.path.join(ut.JOBS_DIR, job_id, "logs",
            #                        f"{job_id}_{program}.log")) as inf:
            #     log_contents = "<br/>".join(inf.readlines())

            return show_template("result_page.html", j_id=job_id,
                                 status=status,
                                 content_size=format_size(size),
                                 module=module,
                                 modules_with_plots=modules_with_plots,
                                 job_title=job.title,
                                 # log_contents=log_contents,
                                 downstream_modules=downstream_modules[module],
                                 connected_jobs=get_connected_jobs(job),
                                 help_enabled=False)

        elif status == "failed":

            return show_template("failed_job.html",
                                 job_title=job.title,
                                 j_id=job_id,
                                 module=job.job_type,
                                 status=status,
                                 failure_reason=get_failure_reason(job_id, module_to_tool[job.job_type]),
                                 help_enabled=False)


        elif status == "queued" or status == "running":

            if "pj" not in request.args:
                pj = "null"
            else:
                pj = request.args["pj"]


            if status == 'queued':
                stages = []
            else:
                stages = get_execution_stages_front_end(
                    job_type=job.job_type,
                    job_id=job_id)

            return show_template("status_page.html", j_id=job_id,
                                 parent_job=pj,
                                 status=status,
                                 store_job_id=store_job_id,
                                 job_title=job.title,
                                 j_type=j_type,
                                 stat_code=302,
                                 stages=stages,
                                 help_enabled=False)

        elif status == "waiting":
            pj = fetch_job_from_db(job_id).depending_on\
                if "pj" not in request.args else request.args["pj"]

            return show_template("status_page.html", j_id=job_id,
                                 status="waiting for preceding job to finish",
                                 parent_job=pj,
                                 job_title=job.title,
                                 store_job_id=store_job_id,
                                 j_type=j_type,
                                 help_enabled=False)
        else:
            raise IOError(f"Incorrect status of job {job_id} in database")

    else:  # indicates no such job exists in the database
        return show_template("job_not_found.html", job_id=job_id)


@result.route("/download/<job_id>", methods=["GET", "POST"])
def return_user_download(job_id: str) -> flask.wrappers.Response:
    """Returns zipped file to client, enabling the user to download the file

    Input:
        - job_id: job ID for which the results are requested

    Output:
        - Downloads zipped file to the client's side. Therefore, the files
            stored on the server are transferred to the client.

    Currently only supports downloading of the .zip file.
    """

    # TODO future: send_from_directory is a safer approach and should be used
    # as Flask should not be serving files when deployed. Actually, NGINX should serve the files
    # result_path =
    path = f'{os.sep}'.join(generate_paths(job_id)[2].split(os.sep)[1:])
    # take results path, and remove first cagecat occurrence as this is also
    # pasted by the send_file function
    return send_file(os.path.join(path, f"{job_id}.zip"))


@result.route("/", methods=["GET", "POST"])
def result_from_job_id() -> t.Union[str, str]: # actual other Union return type
    # is: werkzeug.wrappers.response.Response
    """Shows page for navigating to results page of job ID or that page itself

    Input:
        No inputs

    Output:
        - HTML represented in string format. Renders different templates
            whether the job ID is present in the SQL database or not ("POST"
            request), or the page for entered a job ID is requested ("GET"
            request).

    """
    if request.method == "GET":
        return show_template("result_from_jobid.html", help_enabled=False)
    else:  # can only be POST as GET and POST are the only allowed methods
        job_id = request.form["job_id"]
        if fetch_job_from_db(job_id) is not None:
            return show_template('redirect.html', url=url_for('result.show_result', job_id=job_id))
        else:
            return show_template("job_not_found.html", job_id=job_id)


@result.route("/stage/<job_id>")
def get_execution_stage(job_id: str):
    job = fetch_job_from_db(job_id)
    # main_search_job = job.main_search_job
    # print(job)
    #
    # job_type = job.job_type
    # if job.job_type == 'search' and main_search_job != 'null':
    #     job_type = 'recompute'
    #     print('We changed it!')
    #
    # print('The new job_type is', job_type)
    # print(main_search_job)
    # print(type(main_search_job))
    # print(main_search_job == 'null')
    stages = get_execution_stages_log_descriptors(
        job_type=job.job_type,
        job_id=job.id
    )

    log_base = generate_paths(job_id)[1]
    log_fn = os.path.join(log_base, f'{job_id}.log')

    # queued situation
    # running situation
    with open(log_fn) as inf:
        logs = inf.read()

    data = {
        'finished': -1,
        'total': len(stages)
    }
    print(stages)
    for stage in stages:
        if stage in logs:
            print(stage, 'is in contents')
            data['finished'] += 1

    return json.dumps(data)


@result.route("/plots/<job_id>")
def get_plot_contents(job_id) -> str:
    """Returns the HTML code of a plot as a string

    Input:
        - job_id: job ID for which the plot is requested

    """
    return prepare_finished_result(job_id, fetch_job_from_db(
        job_id).job_type)[0]

# Helper functions
def get_execution_stages_front_end(job_type: str, job_id: str):
    # TODO merge with get_execution_stages_log_descriptors
    log_base = generate_paths(job_id)[1]
    cmd_fp = os.path.join(log_base, f'{job_id}_command.txt')
    with open(cmd_fp) as inf:
        contents = inf.read()

    stages_front_end: list = copy.deepcopy(execution_stages_front_end[job_type])

    if job_type == 'search':
        if '--recompute' in contents:
            stages_front_end: list = copy.deepcopy(execution_stages_front_end['recompute'])
            index = 2
        else:
            index = 5

        if '--intermediate_genes' in contents:
            stages_front_end.insert(index, 'Fetching intermediate genes from NCBI')

    elif job_type == 'extract_sequences':
        if '--extract_sequences' in contents:
            stages_front_end.insert(2, 'Fetch sequences from NCBI')

    return stages_front_end


def get_execution_stages_log_descriptors(job_type: str, job_id: str):
    # TODO merge with get_execution_stages_front_end
    log_base = generate_paths(job_id)[1]
    cmd_fp = os.path.join(log_base, f'{job_id}_command.txt')
    with open(cmd_fp) as inf:
        contents = inf.read()

    stages_log_descriptors: list = copy.deepcopy(execution_stages_log_descriptors[job_type])

    if job_type == 'search':
        if '--recompute' in contents:
            stages_log_descriptors: list = copy.deepcopy(execution_stages_log_descriptors['recompute'])
            index = 2
        else:
            index = 6

        if '--intermediate_genes' in contents:
            stages_log_descriptors.insert(index, 'Searching for intermediate genes')

    elif job_type == 'extract_sequences':
        if '--extract_sequences' in contents:
            stages_log_descriptors.insert(2, 'Querying NCBI')

    return stages_log_descriptors
