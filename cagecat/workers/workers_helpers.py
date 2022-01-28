"""Stores helper functions of the workers.py module

Author: Matthias van den Belt
"""

# package imports
import subprocess
import os

# own project imports
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from cagecat.general_utils import fetch_job_from_db, generate_paths, send_email
from cagecat import db
from config_files.config import cagecat_version, domain
from cagecat.db_models import Job, Statistic
from cagecat.const import genbank_extensions, fasta_extensions

# typing imports
from werkzeug.datastructures import ImmutableMultiDict
import typing as t

# Function definitions
from config_files.sensitive import finished_hmm_db_folder


def create_filtering_command(options: ImmutableMultiDict,
                             is_cluster_related: bool) -> t.List[str]:
    """Forges command for filtering based on submitted options

    Input:
        - options: user submitted parameters via HTML form
        - is_cluster_related: indicates if the filtering command is meant
            for filtering clusters
    """
    partly_cmd = []

    if not is_cluster_related:
        if options["selectedQueries"]:
            partly_cmd.append("--queries")
            partly_cmd.extend(options["selectedQueries"].split())

    if options["selectedOrganisms"]:
        partly_cmd.extend(["--organisms", options['selectedOrganisms']])
        # TODO future: could also that user gives multiple patterns. separated by ;?

    # if options["selectedScaffolds"]:
    #     partly_cmd.append("--scaffolds")
    #     partly_cmd.extend(options["selectedScaffolds"].split())

    if is_cluster_related:
        if options["clusterNumbers"]:
            partly_cmd.append("--clusters")
            partly_cmd.extend(options["clusterNumbers"].strip().split())

        if options["clusterScoreThreshold"]:
            partly_cmd.extend(["--score_threshold",
                               options["clusterScoreThreshold"]])

        partly_cmd.extend(["--maximum_clusters", options["maxclusters"]])

    return partly_cmd


def create_summary_table_commands(
        module: str, options: ImmutableMultiDict) \
        -> t.List[str]:
    """Generates commands for creating a summary table

    Input:
        - module: name of used cblaster module to create commands for.
            Currently available are: ["search", "gne"]
        - options: user submitted options (values) via HTTP form of front-end

    Output:
        - summary_cmds: commands to enable creation of a custom-defined
            summary table

    Depending on the module, a prefix is required for the commands to work.
    """
    summary_cmds = []

    if module == "search":
        prefix = "output_"
    elif module == "gne":
        prefix = ""
    else:
        raise IOError("Invalid module")

    sum_table_delim = options[f"{module}SumTableDelim"]
    if sum_table_delim:  # evalutes to True if not an empty string
        summary_cmds.extend([f"--{prefix}delimiter", sum_table_delim])

    summary_cmds.extend([f"--{prefix}decimals",
                         options[f"{module}SumTableDecimals"]])

    if f"{module}SumTableHideHeaders" in options:
        summary_cmds.append(f"--{prefix}hide_headers")

    return summary_cmds


def run_command(cmd: t.List[str], log_base: str, job_id: str,
                log_output: bool = True) -> int:
    """Executes a command on the command line

    Input:
        - cmd: split command to be executed. All elements in the
            list are joined together with a space to form a full command
        - log_base: base directory for logging. Has the following structure:
            "cagecat/jobs/{job_id}/logs/"
        - job_id: ID corresponding to the job the function is called for

    Output:
        - return_code: exit code of the executed command. A non-zero exit
            code indicates something went wrong. An exit code of 0 indicates
            the command has executed without any problems.

    """
    if log_output:
        log_command(cmd, log_base, job_id)

        with open(os.path.join(log_base, f"{job_id}.log"), "w") as outf:
            try:
                res = subprocess.run(cmd, stderr=outf, stdout=outf, text=True)
                return_code = res.returncode
            except:  # purposely broad except clause to catch all exceptions
                return_code = 1
    else:
        try:
            res = subprocess.run(cmd)
            return_code = res.returncode
        except:  # purposely broad except clause to catch all exceptions
            return_code = 1

    return return_code


def zip_results(job_id: str) -> None:
    """Zips all files belonging to a job (logs, results, uploads)

    Input:
        - job_id: ID corresponding to the job the function is called for

    Output:
        - None
        - A .zip file containing all files which are part of a job

    We change directories to the {job_id} folder, which contains 3 folders:
    1. logs; 2. results; 3. uploads; Therefore, the paths used in this
    function are relative to the {job_id} folder.
    """
    base, log_dir, results_dir = generate_paths(job_id)
    os.chdir(base)  # go 1 level up

    cmd = ["zip", "-r", os.path.join("results", f"{job_id}.zip"), "."]
    # all files and folders in the current directory
    # (cagecat/jobs/{job_id}/ under the base folder

    run_command(cmd, "logs", job_id, log_output=False)
    # invalid path: 'logs/U812J131P392S71_zip.txt/U812J131P392S71_cmd.txt'
    # something is going wrong


def log_command(cmd: t.List[str], log_base: str, job_id: str) -> None:
    """Logs the executed command to a file

    Input:
        - cmd: split command to be executed. All elements in the
            list are joined together with a space to form a full command
        - log_base: base directory for logging. Has the following structure:
            "cagecat/jobs/{job_id}/logs/"
        - job_id: ID corresponding to the job the function is called for

    Output:
        - None
        - .txt file with the executed command
    """
    with open(os.path.join(log_base,
                           f"{job_id}_command.txt"), "w") as outf:
        outf.write(" ".join(cmd))


def pre_job_formalities(job_id: str) -> None:
    """Wrapper function for functions to be executed pre-job execution

    Input:
        - job_id: ID corresponding to the job the function is called for

    Output:
        - None
        - See documentation of executed functions for their corresponding
            outputs
    """
    add_time_to_db(job_id, "start", db)
    mutate_status(job_id, "start", db)


def send_notification_email(job: Job) -> None:
    """Sends notification mail when a job has finished running

    Input:
        - job: a job entry in the SQL database (is an object, stores all
            job-specific details as attributes)

    Output:
        - None, an e-mail being sent to the user-defined e-mail address
    """
    contents = f'''Dear researcher,
    
The job (type: {job.job_type}) you submitted on {job.post_time} has finished running on {job.finish_time}.'''

    contents += f'''

You are able to perform additional downstream analysis by navigating to the results page of your job by going to:\n{domain}results/{job.id}\n
Also, downloading your results is available on this web page.''' \
        if job.status == 'finished' else f'''

To investigate why your job has failed, please visit {domain}results/{job.id}.\nIf the failure reason is unknown, please submit feedback to help us improve CAGECAT.\n'''

    send_email(f'Your job: {job.title}' if job.title else f'Your job with ID {job.id} has {job.status}',
               contents,job.email)


def log_cagecat_version(job_id: str) -> None:
    """Logs the version of CAGECAT to the job's logs folder

    Input:
        - job_id: ID of job for which CAGECAT's version should be logged

    Output:
        - written file with CAGECAT's version

    """
    with open(os.path.join(generate_paths(job_id)[1], 'CAGECAT_version.txt'), 'w') as outf:
        outf.write(f'CAGECAT_version={cagecat_version}')


def post_job_formalities(job_id: str, return_code: int) -> None:
    """Wrapper function for functions to be executed post-job execution

    Input:
        - job_id: ID corresponding to the job the function is called for
        - return_code: exit code of the executed command. A non-zero exit
            code indicates something went wrong. An exit code of 0 indicates
            the command has executed without any problems.

    Output:
        - None
        - See documentation of executed functions for their corresponding
            outputs
    """
    log_cagecat_version(job_id)
    zip_results(job_id)

    j = fetch_job_from_db(job_id)

    add_time_to_db(job_id, "finish", db)
    mutate_status(job_id, "finish", db, return_code=return_code)
    if j.email:
        send_notification_email(j)

    remove_email_from_db(j)
    db.session.commit()


def store_query_sequences_headers(log_path: str, input_type: str, data: str):
    """Saves the submitted query headers to a .csv file

    Input:
        - log_path: path to the log directory of this job
        - input_type: selected input_type by the user
        - data: query headers (NCBI entries) or file_path to the uploaded
            FASTA file

    Output:
        - None, written file
    """
    if input_type == "ncbi_entries":  # ncbi_entries
        headers = data
    elif input_type == "file":
        ext = '.' + data.split('.')[-1]
        if ext in fasta_extensions:
            with open(data) as inf:
                headers = [line.strip()[1:].split()[0] for line in
                           inf.readlines() if line.startswith(">")]
        elif ext in genbank_extensions:
            with open(data) as inf:
                headers = [line.strip().split('"')[1] for line in inf.readlines() if '/protein_id=' in line]
        else:
            raise ValueError(f'Invalid extension: {ext}. Did the user upload a file with dots in it?')

    with open(os.path.join(log_path, "query_headers.csv"), "w") as outf:
        outf.write(",".join(headers))


def forge_database_args(options: ImmutableMultiDict) -> t.List[str]:
    """Forges command for database selection based on submitted options

    Input:
        - options: user submitted parameters via HTML form

    Output:
        - base: appropriate (based on submitted options) argument list
    """

    # TODO future: handle recompute scenario as now mode is always given as remote, which is not always the case. The search type should be fetched from the initial search job
    base = ['--database']
    if options['mode'] in ('hmm', 'combi_remote'):
        splitted = options["selectedGenus"].split('_')
        organism = splitted[0].lower()
        genus_fasta = f'{splitted[1]}.fasta'

        base.append(os.path.join(finished_hmm_db_folder, organism, genus_fasta))

    if options['mode'] in ('remote', 'combi_remote'):
        if 'database_type' in options:
            base.append(options['database_type'])
        else:  # when recomputing it's not there
            return []

    if len(base) not in (2, 3):
        raise IOError('Incorrect database arguments length')

    return base


def log_threshold_exceeded(parameter: int, threshold: int,
                           job_data: t.Tuple[str, str, str],
                           error_message: str) -> bool:
    """Logs an error message if the given threshold was exceeded

    Input:
        - parameter: the given value by the user for a parameter
        - threshold: the corresponding threshold for that parameter
        - job_data: tuple of
            [0]: log_path: path to where log files should be written
            [1]: job_id: id of the job
            [2]: program: name of the used program
        - error_message: message technically describing what is incorrect.
            Is formatted in a user-friendly error description later.

    Output:
        - boolean: whether or not the threshold was exceeded, and the worker
            function from which this function is called should return (exit)

    The logged error message will be used by when the results of a job are
    requested to find the appropriate error message to display to the user.
    """

    if parameter > threshold:
        log_path, job_id, program = job_data
        with open(os.path.join(log_path, f'{job_id}_{program}.log'), 'w') as outf:
            outf.write(f'{error_message} ({parameter} > {threshold})')

        post_job_formalities(job_id, 999)
        return True

    return False


def add_time_to_db(job_id: str, time_type: str, db: SQLAlchemy) -> None:
    """Adds timestamp to job entry with given ID in SQL database

    Input:
        - job_id: ID corresponding to the job the function is called for
        - time_type: column in the SQL table to which a timestamp should be
            added. Available options are: ["start", "finish"]
        - db: SQL database connection with the Flask application

    Output:
        - None
        - Stored time at given column in the SQL database
    """
    job = fetch_job_from_db(job_id)

    formatted_time = datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')
    if time_type == "start":
        job.start_time = formatted_time
    elif time_type == "finish":
        job.finish_time = formatted_time
    else:
        raise IOError("Invalid time type")

    db.session.commit()


def mutate_status(job_id: str, stage: str, db: SQLAlchemy,
                  return_code: t.Optional[int] = None) -> None:
    """Mutates status of job entry with given ID in SQL database

    Input:
        - job_id: ID corresponding to the job the function is called for
        - stage: stage the job has entered. Available options are:
            ["start", "finish"]
        - db: SQL database connection with the Flask application
        - return_code: exit code of the command ran. 0 indicates command
            execution without errors

    Output:
        - None
        - Mutated job status in the SQL database

    Raises:
        - IOError: when the given stage is invalid
    """
    job = fetch_job_from_db(job_id)

    if stage == "start":
        new_status = "running"
    elif stage == "finish":
        if return_code is None:
            raise IOError("Return code should be provided")
        elif not return_code:  # return code of 0
            new_status = "finished"
        else:
            print('Return code is:', return_code)
            new_status = "failed"

        Statistic.query.filter_by(name=new_status).first().count += 1

    else:
        raise IOError("Invalid stage")

    job.status = new_status
    db.session.commit()


def remove_email_from_db(db_job: Job):
    if db_job.email != '':
        db_job.email = '-'
