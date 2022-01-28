"""Module to store functions currently not used for possible future usage

Author: Matthias van den Belt
"""
import re
import typing as t

from cagecat.const import clust_number_with_score_pattern


def parse_selected_scaffolds(selected_clusters: str) -> t.Union[str, None]:
    """Returns scaffolds of the selected clusters

    Input:
        - selected_clusters: user-selected clusters. These clusters are
            separated by "\r\n"

    Output:
        - selected_scaffolds: parsed scaffolds. Is None when no clusters have
            been selected for downstream processing

    """
    if selected_clusters != "No clusters selected":
        selected_scaffolds = []

        for cluster in selected_clusters.split("\n"):
            # TODO future: optimization: use regex here
            sep_index = cluster.find(")") + 1  # due to excluding last index
            # organism = cluster[:sep_index].split("(")[0].strip()
            selected_scaffolds.append(
                cluster[sep_index + 1:].strip())  # due to separation
            # character between organism and scaffold

        selected_scaffolds = "\n".join(selected_scaffolds)
    else:
        selected_scaffolds = None

    return selected_scaffolds


def check_if_already_has_too_few_species(genus):
    try:
        with open('too_few_species.txt') as inf:
            for l in inf.readlines():
                if l.strip().split(',')[0].split()[0] == genus:
                    print(f'         -> Skipping {genus}: (found in too_few_species.txt)')
                    # first split: split organism,gbff_file,md5_file
                    # second split: split organism into genus / species

                    exit(0)

    except FileNotFoundError:
        print(' -> No too_few_species.txt file found')


def parse_selected_cluster_names(selected_clusters: str) \
        -> t.Union[str, None]:
    """Extracts and formats selected clusters in a readable manner

    Input:
        - selected_clusters: user-selected clusters. These clusters are
            separated by "\r\n"

    Output:
        - cluster_names: parsed cluster names. Returns None when no clusters
            were selected. For CORASON, this should never happen, as
            it always needs clusters to search in
    """
    if selected_clusters != "No clusters selected":
        cluster_names = []

        for cluster in selected_clusters.split("\r\n"):
            sep_index = cluster.find(")") + 1
            organism = cluster[:sep_index].split("(")[0].strip()
            clust_num = int(re.findall(clust_number_with_score_pattern, cluster)[0])

            cluster_names.append(f"{organism} (Cluster {clust_num})")

        cluster_names = "\n".join(cluster_names)
    else:
        cluster_names = None

    return cluster_names
