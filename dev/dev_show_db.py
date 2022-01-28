"""Module to show the current database

Author: Matthias van den Belt
"""

# package imports
from sys import argv

# own project imports
from cagecat.db_models import Job, Statistic

### main code
if __name__ == "__main__":
    try:
        if argv[1] == "failed":
            for j in Job.query.filter_by(status="failed").all():
                print(j)
                path = f"cagecat/jobs/{j.job_id}/logs/{j.job_id}_cblaster.log"

                with open(path) as inf:
                    print(inf.readlines())
    except IndexError:
        for j in Job.query.all():
            print(j)

        print(Statistic.query.all())
