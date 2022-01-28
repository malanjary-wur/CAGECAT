"""Helper functions for tool pages

Author: Matthias van den Belt
"""
import os
import re
import typing as t

from more_itertools import consecutive_groups

from cagecat.const import jobs_dir


def read_headers(job_id: str) -> t.List[str]:
    """Reads headers belonging to the search of a job ID

    Input:
        - job_id: id of the job for which the query headers are asked for

    Output:
        - headers: the query headers of this job ID
    """
    with open(os.path.join(jobs_dir, job_id, "logs", "query_headers.csv")) as outf:
        headers = outf.read().strip().split(",")

    return headers


def format_cluster_numbers(cluster_numbers: t.List[int]) -> t.List[str]:
    """Pretty formats the selected cluster numbers in a sorted way

    Input:
        - cluster_numbers: parsed user-selected cluster numbers

    Output:
        - pretty formatted cluster numbers. Consecutive cluster numbers are
            shown in the following way: [3, 2, 1, 8] becomes ["1-3", "8"]
    """
    cluster_numbers.sort()
    groups = [list(g) for g in consecutive_groups(cluster_numbers)]
    return [f"{g[0]}-{g[-1]}" if len(g) != 1 else str(g[0]) for g in groups]


def parse_selected_cluster_numbers(selected_clusters: str,
                                   pattern: str,
                                   format_nicely: bool = True) -> str:
    """Parses the cluster numbers of the user-selected clusters

    Input:
        - selected_clusters: user-selected clusters. These clusters are
            separated by "\r\n"
        - pattern: appropriate pattern to use to parse selected cluster
            numbers. This changes as some modules use a different format
            to show their clusters
        - format_nicely: create nicely formatted (e.g. 1 & 2 & 3 & 5
            becomes 1-3 5) or create a functional format (e.g. 1,2,3,5).
            What is desired is dependent on what code is called after this
            function.

    Output:
        - cluster_numbers: extracted cluster numbers separated by a space.
            Consecutive numbers are merged by the format_cluster_numbers
            function. Example: [1, 8, 3, 2] becomes ["1-3", "8"]. Is an
            empty string when no clusters have been selected. Not None, as
            this value is used to set the value of the input area of
            cluster numbers in HTML.
    """
    if selected_clusters:  # empty string evaluates to False
        cluster_numbers = []

        for cluster in selected_clusters.split("\r\n"):
            cluster_numbers.append(int(re.findall(pattern,
                                                  cluster)[0]))

        if format_nicely:
            cluster_numbers = " ".join(format_cluster_numbers(cluster_numbers))
        else:
            cluster_numbers = ",".join([str(n) for n in cluster_numbers])
    else:
        cluster_numbers = ""

    return cluster_numbers
