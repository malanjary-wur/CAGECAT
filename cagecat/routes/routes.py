"""Stores routes for Flask web application

Author: Matthias van den Belt
"""

# package imports
import copy
from flask import url_for, redirect, request
import os

# own project imports
from cagecat.const import submit_url, extract_clusters_options, jobs_dir, hmm_database_organisms
from cagecat.docs.help_texts import help_texts
from cagecat.general_utils import show_template, get_server_info, fetch_job_from_db

from cagecat import app
from cagecat.classes import CAGECATJob
from cagecat.forms.forms import CblasterSearchBaseForm, CblasterRecomputeForm, CblasterSearchForm, CblasterGNEForm, CblasterExtractSequencesForm, \
    CblasterExtractClustersForm, CblasterVisualisationForm, ClinkerBaseForm, ClinkerDownstreamForm, ClinkerInitialForm, CblasterSearchHMMForm
from cagecat.routes.submit_job_helpers import validate_full_form, generate_job_id, create_directories, prepare_search, get_previous_job_properties, \
    save_file, enqueue_jobs
from config_files.config import cagecat_version
from config_files.sensitive import finished_hmm_db_folder

global available_hmm_databases
# route definitions

@app.route('/cagecat')
def home_page_old_url():
    return redirect(url_for('home_page'))

@app.route('/')
def home_page():
    return show_template('index.html', help_enabled=False)

@app.route('/invalid-submission')
def invalid_submission():
    return show_template('incorrect_submission.html', help_enabled=False)

# exceptions = {
#     'search': [
#         ('database_type', cblaster_search_databases)
#     ],
#     'binary_table': [
#         ('keyFunction', cblaster_search_binary_table_key_functions),
#         ('hitAttribute', cblaster_search_binary_table_hit_attributes)
#     ]
# }

@app.route("/help")
def help_page() -> str:
    """Shows the help page to the user

    Output:
        - HTML represented in string format
    """
    return show_template("help.html", version=cagecat_version, help_enabled=False)


@app.route("/docs/<input_type>")
def get_help_text(input_type):
    """Returns help text corresponding to the requested input parameter

    Input:
        - input_type: HTML name of the input parameter

    Output:
        - help texts of input parameter. Keys: "title", "module", "text"
    """

    if input_type not in help_texts:
        return {'title': 'Missing help text', 'module': '', 'text':
            'This help text is missing. Please submit feedback and indicate'
            ' of which parameter the help text is missing.\n\nThanks in advance.'}

    return help_texts[input_type]


@app.route('/status')
def get_server_status():
    return get_server_info()


@app.route('/update-hmm-databases')
def update_hmm_databases():
    global available_hmm_databases
    # Doesn't have to return anything, only trigger
    all_databases = {}

    for organism_folder in os.listdir(finished_hmm_db_folder):
        genera = set()
        if organism_folder == 'logs':
            continue

        if organism_folder not in hmm_database_organisms:
            return 'Incorrect organism folder in HMM databases'

        organism_path = os.path.join(finished_hmm_db_folder, organism_folder)
        for file in os.listdir(organism_path):
            genus = file.split('.')[0]

            genera.add(genus)

        all_databases[organism_folder.capitalize()] = sorted(list(genera))

    available_hmm_databases = all_databases

    return '1'  # indicating everything went well


# Error handlers
@app.errorhandler(404)
def page_not_found(error):  # should have 1 parameter, doesn't have to be used
    """Shows page displaying that the requested page was not found

    """
    return show_template("page_not_found.html",
                                               stat_code=404,
                                               help_enabled=False)


@app.errorhandler(405)
def invalid_method():
    """Redirects user to home page if method used for request was invalid

    """
    return redirect(url_for("home_page"))


update_hmm_databases()
# within routes.py to prevent circular import (as it was first in const.py).
# Additionally, this variable does not have to be updated manually, and
# is therefore left out of const.py
@app.route(submit_url, methods=["POST"])
def submit_job() -> str:
    """Handles job submissions by putting it onto the Redis queue

    Input:
        No inputs

    Output:
        - redirect to results page of the generated job ID

    Raises:
        - NotImplementedError: when functionality that has not been implented
            yet is called.
        - IOError: failsafe for when for some reason no jobID or sessionFile
            was given
    """
    new_jobs = []

    job_type = request.form["job_type"]
    job_id = generate_job_id()

    # Note that the "{module}PreviousType" is submitted via the form, but is
    # only used if a previous job ID or previous session file will be used

    create_directories(job_id)

    if job_type == "search":
        # first check if the base form is valid
        if not validate_full_form(CblasterSearchBaseForm, request.form):
            return redirect(url_for('invalid_submission'))

        file_path, job_type = prepare_search(job_id, job_type)
        forms_to_validate = []
        if job_type == 'recompute':
            forms_to_validate.append(CblasterRecomputeForm)
        elif job_type == 'search':

            if 'mode' in request.form:
                if request.form['mode'] == 'hmm':
                    forms_to_validate.append(CblasterSearchHMMForm)
                elif request.form['mode'] == 'remote':
                    forms_to_validate.append(CblasterSearchForm)
                elif request.form['mode'] == 'combi_remote':
                    forms_to_validate.extend((CblasterSearchForm, CblasterSearchHMMForm))
                else:
                    raise ValueError('Incorrect mode found:', request.form['mode'])
            else:
                print('No mode found')

        else:
            raise ValueError('Incorrect job type returned')

        for form_type in forms_to_validate:
            if not validate_full_form(form_type, request.form):
                return redirect(url_for('invalid_submission'))

        new_jobs.append(CAGECATJob(job_id=job_id,
                                   options=request.form,
                                   job_type=job_type,
                                   file_path=file_path))

    elif job_type == "gne":
        if not validate_full_form(CblasterGNEForm, request.form):
            return redirect(url_for('invalid_submission'))

        new_jobs.append(CAGECATJob(job_id=job_id,
                                   options=request.form,
                                   file_path=get_previous_job_properties(job_id, job_type, "gne")))

    elif job_type == "extract_sequences":
        # For now, only when coming from a results page (using a previous job
        # id) is supported
        if not validate_full_form(CblasterExtractSequencesForm, request.form):
            return redirect(url_for('invalid_submission'))

        new_jobs.append(CAGECATJob(job_id=job_id,
                                   options=request.form,
                                   file_path=os.path.join(jobs_dir,
                                                          request.form['prev_job_id'],
                                              "results",
                                              f"{request.form['prev_job_id']}_session.json")))

    elif job_type == "extract_clusters":
        if not validate_full_form(CblasterExtractClustersForm, request.form):
            return redirect(url_for('invalid_submission'))

        prev_job_id = fetch_job_from_db(
            request.form["prev_job_id"]).main_search_job

        if prev_job_id == "null":
            prev_job_id = request.form["prev_job_id"]
        # For now, only when coming from a results page (using a previous job
        # id) is supported

        new_jobs.append(CAGECATJob(job_id=job_id,
                                   options=request.form,
                                   file_path=os.path.join(jobs_dir,
                                                          prev_job_id,
                                              "results",
                                              f"{prev_job_id}_session.json")))

    elif job_type == "clinker_query":
        if not validate_full_form(CblasterVisualisationForm, request.form):
            return redirect(url_for('invalid_submission'))

        new_jobs.append(CAGECATJob(job_id=job_id,
                                   options=request.form,
                                   file_path=os.path.join(jobs_dir,
                                                          request.form['prev_job_id'],
                                                          "results",
                                                          f"{request.form['prev_job_id']}_session.json")))

    # elif job_type == "corason":
    #     extr_clust_options = copy.deepcopy(co.EXTRACT_CLUSTERS_OPTIONS)
    #     clust_numbers = dict(request.form)
    #
    #     extr_clust_options['clusterNumbers'] = \
    #         clust_numbers['selectedClustersToUse'] + f' {request.form["selectedReferenceCluster"]}' # as we also need the cluster file for the reference bgc
    #
    #     # TODO future: extract query sequence
    #
    #     new_jobs.append(CAGECATJob(job_id=job_id,
    #                                options=extr_clust_options,
    #                                job_type='extract_clusters',
    #                                file_path=os.path.join(ut.JOBS_DIR,
    #                                       request.form['prev_job_id'],
    #                                       "results",
    #                                       f"{request.form['prev_job_id']}_session.json")))
    #
    #     new_jobs.append(CAGECATJob(job_id=ut.generate_job_id(),
    #                                options=request.form,
    #                                file_path='TODOCORASONPATH',
    #                                depends_on_job_id=new_jobs[-1].job_id))  # get the last CAGECATJob object
    #
    #     # TODO future: file path corason --> for corason, the file path is the path to where the extracted clusters will be

    elif job_type == "clinker":
        if not validate_full_form(ClinkerBaseForm, request.form):
            return redirect(url_for('invalid_submission'))

        if 'clinkerEnteredJobId' in request.form:  # indicates it was downstream
            if not validate_full_form(ClinkerDownstreamForm, request.form):
                return redirect(url_for('invalid_submission'))

            prev_job_id = request.form["clinkerEnteredJobId"]

            if fetch_job_from_db(prev_job_id).job_type == 'extract_clusters':
                genome_files_path = os.path.join(jobs_dir, prev_job_id, "results")
                depending_on = None
            else:
                new_jobs.append(CAGECATJob(job_id=job_id,
                                           options=copy.deepcopy(extract_clusters_options),
                                           job_type='extract_clusters',
                                           file_path=os.path.join(jobs_dir,
                                                                  prev_job_id,
                                                                  "results",
                                                                  f"{prev_job_id}_session.json")))

                genome_files_path = os.path.join(jobs_dir, job_id, "results")
                depending_on = new_jobs[-1].job_id

        elif request.files:  # started as individual tool
            if not validate_full_form(ClinkerInitialForm, request.form):
                return redirect(url_for('invalid_submission'))

            for f in request.files.getlist('fileUploadClinker'):
                if f.filename:
                    save_file(f, job_id)
                    genome_files_path = os.path.join(jobs_dir, job_id, "uploads")
                else: # indicates the example was posted
                    genome_files_path = os.path.join('cagecat', 'example_files')
            depending_on = None

        else:
            raise ValueError('Incorrect submitted options (clinker)')

        new_jobs.append(CAGECATJob(job_id=job_id if depending_on is None else generate_job_id(),
                                   options=request.form,
                                   file_path=genome_files_path,
                                   depends_on_job_id=depending_on))

    else:  # future input types
        raise NotImplementedError(f"Module {job_type} is not implemented yet in submit_job")

    last_job = fetch_job_from_db(enqueue_jobs(new_jobs))

    url = url_for("result.show_result",
                  job_id=last_job.id,
                  pj=last_job.depending_on,
                  store_job_id=True,
                  job_title=last_job.title,
                  email=last_job.email,
                  j_type=last_job.job_type)

    return show_template('redirect.html', url=url)
