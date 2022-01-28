FROM ubuntu:latest
FROM python:3

RUN apt-get update
RUN apt-get install -y supervisor redis zip hmmer nginx systemd nano htop cron ncdu ncbi-entrez-direct diamond-aligner
RUN pip3 install rq Flask more_itertools Flask_SQLAlchemy redis Werkzeug clinker uWSGI wtforms

RUN git clone https://github.com/gamcil/cblaster.git && cd cblaster/ && pip install .

COPY repo/ /repo/

RUN mkdir /backups
RUN mkdir -p /process_logs/maintenance
RUN mkdir /pfam_db
RUN mkdir -p /root/.config/cblaster

RUN mv /repo/config_files/cagecat /etc/nginx/sites-available/cagecat
RUN mv /repo/config_files/config.ini /root/.config/cblaster/config.ini

# We don't have to copy uwsgi_params, as in cagecat the /repo/config_files/uwsgi_params file is referenced to

RUN ln -s /etc/nginx/sites-available/cagecat /etc/nginx/sites-enabled

RUN chmod +x /repo/maintenance/maint_backup.sh
RUN chmod +x /repo/hmm_database_creation/construct_hmm_databases.sh
RUN chmod +x /repo/maintenance/maint_remove_old_jobs.py
RUN chmod +x /repo/hmm_database_creation/create_databases.py

RUN mv /repo/config_files/crontab /etc/crontab

CMD ["/usr/bin/supervisord", "-c", "/repo/config_files/supervisord.conf"]
