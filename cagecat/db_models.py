"""Stores models of entities for SQL database interacted by with SQLAlchemy

Author: Matthias van den Belt
"""
# package imports
from datetime import datetime

# own project imports
from cagecat import db

## SQLAlchemy database classes
class Job(db.Model):
    """Model for creating a job entry

        Inherits from db.Model
    """
    id = db.Column(db.String(15), primary_key=True)
    job_type = db.Column(db.String(10), nullable=False)
    redis_id = db.Column(db.String(80))
    status = db.Column(db.Text, nullable=False)

    # user-specified items
    title = db.Column(db.String(60))
    email = db.Column(db.String(100))

    # connecting jobs
    main_search_job = db.Column(db.String(15))
    child_jobs = db.Column(db.String(), default="")
    depending_on = db.Column(db.String(10))

    # timing
    post_time = db.Column(db.String(), nullable=False, default=datetime.utcnow().strftime('%B %d %Y - %H:%M:%S'))
    start_time = db.Column(db.String())
    finish_time = db.Column(db.String)

    def __repr__(self):
        # print("Main search", self.main_search_job)
        # print("Children", self.child_jobs)
        # print("Depending", self.depending_on)
        return f"ID: {self.id}; Type: {self.job_type}; " \
               f"Status: {self.status}; " \
               f"Finished: {self.finish_time}; Main job{self.main_search_job}"

class Statistic(db.Model):
    """Model for creating a entry for job statistics

    Inherits from db.Model

    """
    # Implemented as counters instead of querying the full db, which could
    # take a long time when the db becomes large

    name = db.Column(db.String(20), primary_key=True)
    count = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"{self.name.capitalize()}: {self.count} jobs"
