#!/bin/bash
# Author: Matthias van den Belt

container_name="cagecat_service"

echo "--> Copying jobs folder and database.db to host"
docker cp cagecat_service:/repo/cagecat/database.db database.db
#docker cp cagecat_service:/repo/cagecat/jobs jobs

echo "--> Cloning new repo"
git clone git@git.wur.nl:belt017/thesis_repo.git && \
mv thesis_repo/ repo

echo "--> Stopping container $container_name"
docker container stop $container_name

echo "--> Copying files from host to container"
# as there is no /repo/cagecat/database.db and
# no /repo/cagecat/jobs on the git repo, these are unaffected.
# Nevertheless, we created a backup of them earlier
docker cp repo cagecat_service:/

echo "--> Starting container $container_name"
docker container start $container_name

echo "Restarting uwsgi"
docker exec cagecat_service uwsgi --reload /tmp/uwsgi-master.pid

echo " -> Old files of files that had their name CHANGED are still present"
echo " -> and should be removed manually"

echo "Done!"
