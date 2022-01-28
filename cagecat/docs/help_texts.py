""""Stores help texts shown to the user when the help-button is clicked

These dictionaries are referenced to when a request is made to the help-text
URL with the key name in that URL to get the appropriate help text. After
changes have been made to this module, uWSGI should be reloaded using:

uwsgi --reload /tmp/uwsgi-master.pid

within the Docker container

Author: Matthias van den Belt
"""

from cagecat.const import fasta_extensions, genbank_extensions

job_details = {'job_title': {'title': 'Job title', 'module': '', 'text': 'Enter a job title for easy identification of jobs.\n\nRequired: no\n\nMaximum length: 60 characters'},
                        'email_notification': {'title': 'Email notification', 'module': '', 'text': 'Enter your e-mail to get notified when your job has finished. Your e-mail will be removed from our servers after one notification mail.\n\nRequired: no'}}

general = {'generalEnteredJobId': {'title': 'Previous job ID', 'module': '', 'text': 'The ID of the job which\' results are wished to be used.'},
                 'generalDelimiter': {'title': 'Output file delimiter', 'module': '', 'text': 'Single delimiter character to use when writing results to a file.\n\nResults will be separated of each other in the output file by the specified character.\n\nRequired: no\nDefault: no delimiter (human readable)'},
                 'generalDecimals': {'title': 'Number of decimals', 'module': '', 'text': 'Total decimal places to use when saving score values.\n\nRequired: yes'},
                 'generalHideHeaders': {'title': 'Hide headers', 'module': '', 'text': 'Hide headers when saving result output.\n\nRequired: no'}}

cblaster_search = {'genomeFile': {'title': 'Query file', 'module': '', 'text': 'File containing protein sequences (FASTA) or a genome (GenBank) to be searched.\n\nAllowed extensions:\n  - ' + '\n  - '.join(fasta_extensions + genbank_extensions)},
                'ncbiEntriesTextArea': {'title': 'Search from NCBI entries', 'module': '', 'text': 'A collection of valid NCBI sequence identifiers to be searched.\n\nNCBI identifiers should be separated by a newline (enter).\n\nEntering the same identifier twice will prevent you from continuing.'},
                'entrez_query': {'title': 'Filter using Entrez query', 'module': '', 'text': 'An NCBI Entrez search term for pre-search filtering of an NCBI database when using command line BLASTp (e.g. Aspergillus[organism])\n\nRequired: no'},
                'database_type': {'title': 'Database to search in', 'module': '', 'text': 'Database to be searched: NCBI database name.\n\nRequired: yes'},
                'max_hits': {'title': 'Maximum hits to show', 'module': '', 'text': 'Maximum total hits to save from a remote BLAST search. Setting this value too low may result in missed hits/clusters.\n\nRequired: yes'},
                'max_evalue': {'title': 'Maximum e-value', 'module': '', 'text': 'Maximum e-value for a BLAST hit to be saved.\n\nRequired: yes'},
                'min_identity': {'title': 'Minimum percent identity', 'module': '', 'text': 'Minimum percent identity for a BLAST hit to be saved.\n\nRequired: yes'},
                'min_query_coverage': {'title': 'Minimum query coverage', 'module': '', 'text': 'Minimum percent query coverage for a BLAST hit to be saved.\n\nRequired: yes'},
                'max_intergenic_gap': {'title': 'Maximum intergenic distance between genes', 'module': '', 'text': 'Maximum allowed intergenic distance (bp) between conserved hits to be considered in the same block.\n\nIf you are not sure which value to use, please refer to the Gene Neighbourhood Estimation documentation, as this will help you find a proper value.\n\nRequired: yes\nDefault value: 20000'},
                'percentageQueryGenes': {'title': 'Minimum % of query genes present', 'module': '', 'text': 'Filter on % of query genes needed to be present in cluster\n\nRequired: yes'},
                'min_unique_query_hits': {'title': 'Minimum unique query sequences', 'module': '', 'text': 'Minimum number of unique query sequences that must be conservedin a hit cluster.\n\nRequired: yes'},
                   'min_hits_in_clusters': {'title': 'Minimum hit number in clusters', 'module': '', 'text': 'Minimum number of hits in a cluster.\n\nRequired: yes'},
                   'requiredSequencesSelector': {'title': 'Required sequences in a cluster', 'module': '', 'text': 'Names of query sequences that must be represented in a hit cluster.\n\nOnce you upload a query file or enter NCBI entries, click a sequence header to select it. Hold CTRL while clicking to select multiple sequences. To unselect a header, hold CTRL while clicking the header.\n\nRequired: no\nDefault: none selected'},
                   'sortClusters': {'title': 'Sort output clusters', 'module': '', 'text': 'Sorts the clusters of the final output on score. This means that clusters of the same organism are not necessarily close together in the output.\n\nRequired: no'},
                   'intermediate_genes': {'title': 'Show intermediate genes', 'module': '', 'text': 'Show genes that in or near clusters but not part of the cluster.\n\nRequired: no'},
                   'intermediate_max_distance': {'title': 'Maximum intermediate gene distance', 'module': '', 'text': 'The maximum distance between the start/end of a cluster and an intermediate gene\n\nSetting this to a higher value will allow for a broader analysis of the genome neighbourhood of each cluster.\n\nRequired: yes'},
                   'intermediate_max_clusters': {'title': 'Maximum number of clusters to find intermediate genes for', 'module': '', 'text': 'The maximum amount of clusters will get intermediate genes assigned. Ordered on score.\n\nRequired: yes'}}

cblaster_gne = {'max_intergenic_distance': {'title': 'Maximum intergenic distance', 'module': '', 'text': 'Maximum distance in bp between genes.\n\nRequired: yes'},
             'sample_number': {'title': 'Number of samples', 'module': '', 'text': 'Total samples taken from Maximum intergenic distance.\n\nRequired: yes'},
             'sampling_space': {'title': 'Sampling space', 'module': '', 'text': 'Draw sampling values from a linear or log scale.\n\nRequired: yes'}}

clinker = {
    'noAlign': {
        'title': 'Do not align clusters',
        'module': '',
        'text': 'Do not align clusters.\n\nRequired: no'
    },
    'identity': {
        'title': 'Minimum alignment sequence identity',
        'module': '',
        'text': 'Minimum alignment sequence identity.\n\nRequired: yes'
    },
                      'hideLinkHeaders': {'title': 'Hide alignment column headers', 'module': '', 'text': 'Hide alignment column headers.\n\nRequired: no'},
                      'hideAlignHeaders': {'title': 'Hide alignment cluster name headers', 'module': '', 'text': 'Hide alignment cluster name headers.\n\nRequired: no'},
                      'useFileOrder': {'title': 'Maintain order of input files', 'module': '', 'text': 'Display clusters in order of input files.\n\nRequired: no'},
                 'fileUploadClinker': {
                     'title': 'Genome file(s)',
                     'module': '',
                     'text': 'One or more genome (GenBank) files to be searched.\n\nAllowed extensions:\n  - ' + '\n  - '.join(genbank_extensions)},
                 }

cblaster_search_binary_table = {'keyFunction': {'title': 'Key function', 'module': '', 'text': 'Key function used when generating binary table cell values.\n\nRequired: yes'},
                      'hitAttribute': {'title': 'Hit attribute', 'module': '', 'text': 'Hit attribute used when generating binary table cell values.\n\nRequired: yes'}}

cblaster_search_filtering = {'selectedOrganisms': {'title': 'Organisms to filter fot', 'module': '', 'text': 'Organism names to filter hits for. When entering multiple organisms, separate by a space.\n\nRequired: no'},
                             # 'selectedScaffolds': {'title': '', 'module': '', 'text': ''},
                   'clusterNumbers': {'title': 'Cluster numbers', 'module': '', 'text': 'Cluster numbers/ranges provided by the summary file of the \'search\' command or selected online. If no numbers are entered, no filtering takes place.\n\nRequired: no'},
                   'clusterScoreThreshold': {'title': 'Cluster score threshold', 'module': '', 'text': 'Minimum score of a cluster in order to be included. If no score is entered, no filtering takes place.\n\nRequired: no'},
                   'selectedQueries': {'title': 'Query filtering', 'module': '', 'text': 'IDs of query sequences to filter for.\n\nRequired: no'}}

cblaster_plot_clusters = {'maxclusters': {'title': 'Maximum number of clusters to plot', 'module': '', 'text': 'The maximum amount of clusters that will be plotted. Ordered on score.\n\nRequired: yes'}}

cblaster_extract_sequences = {'downloadSeqs': {'title': 'Download sequences', 'module': '', 'text': 'Download protein sequences for the selected proteins. The resulting summary will have a FASTA format.\n\nRequired: no'},
                   'nameOnly': {'title': 'Name only', 'module': '', 'text': 'Do not save sequence descriptions (i.e. no genomic coordinates).\n\nRequired: no'}}

cblaster_extract_clusters = {'prefix': {'title': 'File prefix', 'module': '', 'text': 'Start of the name for each created cluster file, e.g. <prefix>cluster1.\n\nRequired: no'},
                    'format': {'title': 'File format', 'module': '', 'text': 'Format of the resulting files.\n\nRequired: no'}}

# CORASON_HELPS = {'selectedQuery': {'title': 'Selected query', 'module': '', 'text': 'Query to be analyzed\n\nRequired: yes'},
#                  'selectedReferenceCluster': {'title': 'Selected reference cluster', 'module': '', 'text': 'The cluster number of which cluster should act as the reference cluster. The cluster numbers correspond with the cluster numbers of the preceding job. Note that the reference cluster must include the query gene, or Corason will fail to execute.\n\nRequired: yes'},
#                  'selectedClustersToSearch': {'title': 'Selected clusters to search in', 'module': '', 'text': 'TODO'}, # is this list parameter?
#                  'evalue': {'title': 'Minimal e-value', 'module': '', 'text': 'Minimal e-value for a gene to be considered a hit.\n\nRequired: yes'},
#                  'bitscore': {'title': 'Bitscore', 'module': '', 'text': 'TODO'},
#                  'clusterRadio': {'title': 'Number of genes to analyze', 'module': '', 'text': 'Number of genes in the neighbourhood to analyze\n\nRequired: yes'},
#                  'ecluster': {'title': 'e-value of genes from reference cluster', 'module': '', 'text': 'e-value for sequences from reference cluster\n\nRequired: yes'},
#                  'ecore': {'title': 'TODO', 'module': '', 'text': 'e-value for Best Bidirectional Hits used to construct genomic core from clusters.\n\nRequired: yes'},
#                  'rescale': {'title': 'Rescale', 'module': '', 'text': 'Increasing this number will show a bigger cluster region with smaller genes.\n\nRequired: no?'}}

cblaster_search_hmm_mode  = {'selectedGenus': {'title': 'Selected genus', 'module': '', 'text': 'Genus-specific database to search in. The database is constructed of all representative or reference genomes of the selected genus.\n\nRequired: yes'},
              'hmmProfiles': {'title': 'HMM profiles', 'module': '', 'text': 'HMM profile identifiers to use when searching the selected genus database.\n\nRequired: yes'}}

all_helps = [('multiple', job_details),
             ('multiple', general), ('search', cblaster_search),
             ('neighbourhood', cblaster_gne), ('clinker visualisation', clinker),
             ('search', cblaster_search_binary_table), ('multiple', cblaster_search_filtering),
             ('clinker visualisation with query', cblaster_plot_clusters), ('extract sequences',
                                                                                cblaster_extract_sequences), ('extract clusters', cblaster_extract_clusters),
             ('HMM', cblaster_search_hmm_mode),
             # ('corason', CORASON_HELPS)
             ]
help_texts = {}

# BLANC: {'input_help': {'title': 'blanc', 'module': '', 'text': 'blanc'}}

for label, d in all_helps:
    for key in d:
        d[key]['module'] = label

    help_texts.update(d)
