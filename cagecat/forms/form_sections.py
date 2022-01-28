"""Stores sections of larger forms

Author: Matthias van den Belt
"""

from wtforms import StringField, EmailField, HiddenField, SelectField, IntegerField, DecimalField, SelectMultipleField, BooleanField, SubmitField, \
    MultipleFileField, RadioField, FileField, TextAreaField
from wtforms import Form, validators as val

# name and id are set to the variable name
# description equals the corresponding help text word
from cagecat.const import genbank_extensions, fasta_extensions
from cagecat.forms.valid_input_cblaster import is_safe_string_value

cblaster_search_search_modes = [
    'remote',
    'hmm',
    'combi_remote'
]

cblaster_search_databases = [
    ('nr', 'nr'),
    ('refseq_protein', 'Refseq protein'),
    ('swissprot', 'Swissprot'),
    ('pdbaa', 'pdbaa')
]

cblaster_search_binary_table_key_functions = [
    ('len', 'len'),
    ('sum', 'sum'),
    ('max', 'max')
]

cblaster_search_binary_table_hit_attributes = [
    ('identity', 'identity'),
    ('coverage', 'coverage'),
    ('bitscore', 'bitscore'),
    ('evalue', 'evalue')
]

cblaster_gne_sampling_spaces = [
    ('linear', 'linear'),
    ('log', 'log')
]

cblaster_extract_clusters_formats = [
    ('genbank', 'GenBank'),
    ('bigscape', 'BiG-SCAPE')
]

# general sections
class SubmitForm(Form):
    submit = SubmitField(
        default='Submit',
        render_kw={
            'class': 'button'
        }
    )

class JobInfoForm(Form):
    job_title = StringField(
        label=u'Job title',
        validators=[val.length(max=60), is_safe_string_value],
        description='job_title',
        render_kw={
            'class': ' ',
            'placeholder': 'Experiment number'
        }
    )

    mail_address = EmailField(
        label=u'Email address for notification',
        validators=[val.length(max=100)],
        description='email_notification',
        render_kw={
            'class': ' ',
            'placeholder': 'username@institution.com'
        }
    )

# cblaster input
class InputSearchModeForm(Form):
    # raise NotImplementedError()
    # TODO: implement in future
    mode = RadioField(
        label=u'Remote',
        validators=[], # TODO: check,
        choices=cblaster_search_search_modes
    )


class InputRemoteTypeForm(Form):
    # raise NotImplementedError()

    # File / NCBI entries radio buttons
    pass

class InputSearchRemoteInputTypeFile(Form):
    _all_suffixes = list(genbank_extensions)
    _all_suffixes.extend(fasta_extensions)

    genomeFiles = FileField(
        label=u'Query file*',
        validators=[val.optional()],  # TODO: safe filename
        description='genomeFile',
        render_kw={
            'accept': ','.join(_all_suffixes),
            'onchange': 'readFileContents()',
            'required': ''
        }
    )

class InputSearchRemoteInputTypeNCBIEntries(Form):
    ncbiEntriesTextArea = TextAreaField(
        label=u'NCBI accession number(s)*',
        validators=[is_safe_string_value],
        render_kw={
            'rows': 6,
            'cols': 25,
            'class': 'ncbi-entries',
            'placeholder': 'NCBI accessions',
            'onfocusout': 'validateNCBIEntries()',
            # 'required': '',
            'disabled': 'disabled'
        }
    )


class InputHMMForm(Form):
    # TODO: add to WTForms in future. Circular import now with PRESENT_HMM_DATABASES
    # selectedGenus = SelectField(
    #     label=u'Genus*',
    #     validators=[is_safe_string_value],
    #     description='selectedGenus',
    #     choices=[(genus, genus) for genus in PRESENT_HMM_DATABASES],
    #     render_kw={
    #         'required': ''
    #     }
    # )

    hmmProfiles = TextAreaField(
        label=u'HMM profiles*',
        validators=[is_safe_string_value],
        description='hmmProfiles',
        render_kw={
            'required': '',
            'rows': 6,
            'cols': 25,
            'placeholder': 'HMM profile identifiers'
        }
    )

# cblaster search
class SearchSectionForm(Form):
    entrez_query = StringField(
        label=u'Entrez query',
        validators=[is_safe_string_value],
        description='entrez_query',
        render_kw={
            'placeholder': 'Aspergillus[organism]'
        }
    )

    database_type = SelectField(
        # TODO: when other values than choices are posted, check if it raises error
        label=u'Database',
        validators=[val.input_required(), is_safe_string_value],
        description='database_type',
        choices=cblaster_search_databases,
        render_kw={
            'class': 'select-options'
        }
    )

    hitlist_size = IntegerField(
        label=u'Maximum hits',
        validators=[val.input_required(), is_safe_string_value],
        description='max_hits',
        default=500,
        id='max_hits',
        render_kw={
            'min': 1,
            'max': 10000,
            'step': 1
        }
    )

class FilteringSectionForm(Form):
    max_evalue = DecimalField(
        label=u'Max. e-value',
        validators=[val.input_required(), is_safe_string_value, val.number_range(min=0, max=100)],  # having min=0.01 resulted in an error (Number must be between 0.01 and 100.) during validation
        description='max_evalue',
        default=0.01,
        render_kw={
            'min': 0.01,
            'step': 0.01
        }
    )

    min_identity = IntegerField(
        label=u'Min. identity (%)',
        validators=[val.input_required(), is_safe_string_value, val.number_range(min=0, max=100)],
        description='min_identity',
        default=30,
        render_kw={
            'step': 1
        }
    )

    min_query_coverage = IntegerField(
        label=u'Min. query coverage (%)',
        validators=[val.input_required(), is_safe_string_value, val.number_range(min=0, max=100)],
        description='min_query_coverage',
        default=50,
        render_kw={
            'step': 1
        }
    )

class ClusteringSectionForm(Form):
    max_intergenic_gap = IntegerField(
        label=u'Max. intergenic gap',
        validators=[val.input_required(), is_safe_string_value, val.number_range(min=0, max=1000000)],
        description='max_intergenic_gap',
        default=20000,
        render_kw={
            'step': 1
        }
    )

    percentageQueryGenes = IntegerField(
        label=u'Percentage',
        validators=[val.input_required(), is_safe_string_value],
        description='percentageQueryGenes',
        default=50,
        render_kw={
            'min': 0,
            'max': 100,
            'step': 1
        }
    )

    min_unique_query_hits = IntegerField(
        label=u'Min. unique query hits',
        validators=[val.input_required(), is_safe_string_value],
        description='min_unique_query_hits',
        default=3,
        render_kw={
            'min': 0,
            'max': 150,
            'step': 1
        }
    )

    min_hits_in_clusters = IntegerField(
        label=u'Min. hits in clusters',
        validators=[val.input_required(), is_safe_string_value],
        description='min_hits_in_clusters',
        default=3,
        render_kw={
            'min': 0,
            'max': 150,
            'step': 1
        }
    )

    requiredSequencesSelector = SelectMultipleField(
        label=u'Required sequences',
        validators=[is_safe_string_value],
        description='requiredSequencesSelector',
        choices=[],
        validate_choice=False,  # as this is generated dynamically
        render_kw={
            'style': 'width: 60%;'
        }
    )

    requiredSequences = HiddenField(
        validators=[is_safe_string_value],
        render_kw={
            'value': ''
        }
    )

def get_table_form(module: str, table_type: str):

    prefix = f'{module}{table_type}'

    delimiter = StringField(
        label=u'Delimiter',
        validators=[val.length(max=1), val.Optional(), is_safe_string_value],
        description='generalDelimiter',
        id=f'{prefix}TableDelim',
        name=f'{prefix}TableDelim',
        render_kw={
            'size': 1,
            'class': 'short'
        }
    )

    decimals = IntegerField(
        label=u'Decimals',
        validators=[val.input_required(), is_safe_string_value, val.number_range(min=0, max=9)],
        description='generalDecimals',
        default=2,
        id=f'{prefix}TableDecimals',
        name=f'{prefix}TableDecimals',
        render_kw={
            'step': 1,
            'class': 'short'
        }
    )

    hide_headers = BooleanField(
        label=u'Hide headers',
        validators=[], # TODO: add boolean validators
        description='generalHideHeaders',
        id=f'{prefix}TableHideHeaders',
        name=f'{prefix}TableHideHeaders'
    )

    return delimiter, decimals, hide_headers


class SummaryTableForm(Form):
    delimiter, searchSumTableDecimals, hide_headers = get_table_form('search', 'Sum')


class BinaryTableForm(Form):
    delimiter, searchBinTableDecimals, hide_headers = get_table_form('search', 'Bin')

    keyFunction = SelectField(
        label=u'Key function',
        validators=[val.InputRequired(), is_safe_string_value],
        description='keyFunction',
        choices=cblaster_search_binary_table_key_functions,
        render_kw={
            'onChange': 'changeHitAttribute()',
            'class': 'select-options'
        }
    )

    hitAttribute = SelectField(
        label=u'Hit attribute',
        validators=[val.optional(), is_safe_string_value],
        description='hitAttribute',
        choices=cblaster_search_binary_table_hit_attributes,
        render_kw={
            'disabled': '',
            'class': 'select-options'
        }
    )


class AdditionalOptionsSectionForm(Form):
    sortClusters = BooleanField(
        label=u'Sort clusters',
        validators=[], # TODO: add boolean validator
        description='sortClusters'
    )

class IntermediateGenesSectionForm(Form):
    intermediate_genes = BooleanField(
        label=u'Find intermediate genes',
        validators=[], # TODO: add boolean validator
        description='intermediate_genes',
        render_kw={
            'onclick': "toggleDisabled('intermediate_max_distance', 'intermediate_max_clusters')"
        }
    )

    intermediate_max_distance = IntegerField(
        label=u'Max. distance',
        validators=[is_safe_string_value, val.number_range(min=0, max=250000)],
        description='intermediate_max_distance',
        default=5000,
        render_kw={
            'disabled': ''
        }
    )

    intermediate_max_clusters = IntegerField(
        label=u'Max. clusters',
        validators=[is_safe_string_value, val.number_range(min=1, max=100)],
        description='intermediate_max_clusters',
        default=100,
        render_kw={
            'disabled': ''
        }
    )





    # TODO: multiple selection form: https://wtforms.readthedocs.io/en/2.3.x/fields/#wtforms.fields.SelectMultipleField

# cblaster gne sections
class SummaryTableGNEForm(Form):
    delimiter, searchSumTableDecimals, hide_headers = get_table_form('gne', 'Sum')

class AdditionalOptionsGNEForm(Form):
    max_intergenic_distance = IntegerField(
        label=u'Max. intergenic distance',
        validators=[val.input_required(), val.number_range(min=0, max=2500000), is_safe_string_value],
        description='max_intergenic_distance',
        default=100000,
        render_kw={
            'step': 1
        }
    )

    sample_number = IntegerField(
        label=u'Number of samples',
        validators=[val.input_required(), val.number_range(min=2, max=300), is_safe_string_value],
        description='sample_number',
        default=100,
        render_kw={
            'step': 1
        }
    )

    sampling_space = SelectField(
        label=u'Sampling space',
        validators=[val.input_required(), is_safe_string_value],
        description='sampling_space',
        choices=cblaster_gne_sampling_spaces,
        render_kw={
            'class': 'select-options'
        }
    )

# cblaster extract sequences sections
class ExtractSequencesFilteringForm(Form):
    selectedOrganisms = StringField(
        label=u'Organisms',
        validators=[is_safe_string_value],
        description='selectedOrganisms',
        render_kw={
            'placeholder': 'Organisms to filter for'
        }
    )

    selectedQueries = HiddenField(
        default=''
    )


class ExtractSequencesOutputForm(Form):
    outputDelimiter = StringField(
        label=u'Delimiter',
        validators=[val.length(max=1), val.Optional(), is_safe_string_value],
        description='generalDelimiter',
        render_kw={
            'class': 'short'
        }
    )

    downloadSeqs = BooleanField(
        label=u'Download sequences',
        validators=[], # TODO: add boolean validator
        description='downloadSeqs'
    )

    nameOnly = BooleanField(
        label=u'Name only',
        validators=[], # TODO: add boolean validator
        description='nameOnly'
    )

# cblaster search extract clusters section
class ClustersFilteringForm(Form):
    selectedOrganisms = StringField(
        label=u'Organisms',
        validators=[is_safe_string_value],
        description='selectedOrganisms',
        render_kw={
            'placeholder': 'Organisms to filter for'
        }
    )

    clusterNumbers = StringField(
        label=u'Clusters',
        validators=[is_safe_string_value],
        description='clusterNumbers',
        # default='',
        render_kw={
            'readonly': ''
        }
    )

    clusterScoreThreshold = DecimalField(
        label=u'Score threshold',
        validators=[is_safe_string_value, val.optional()],
        description='clusterNumbers',
        render_kw={
            'step': 0.001
        }
    )


class ExtractClustersOutputForm(Form):
    prefix = StringField(
        label=u'Prefix',
        validators=[is_safe_string_value, val.length(max=15)],
        description='prefix',
        render_kw={
            'class': 'custom-width'
        }
    )

    format = SelectField(
        label=u'Format',
        validators=[is_safe_string_value, val.input_required()],
        description='format',
        choices=cblaster_extract_clusters_formats,
        render_kw={
            'class': 'custom-width'
        }
    )

    maxclusters = IntegerField(
        label=u'Maximum clusters',
        validators=[is_safe_string_value, val.number_range(min=1, max=150), val.input_required()],
        description='maxclusters',
        default=50,
        render_kw={
            'class': 'short',
            'step': 1
        }
    )

class CblasterVisualisationOutputForm(Form):
    maxclusters = IntegerField(
        label=u'Maximum clusters',
        validators=[is_safe_string_value, val.number_range(min=1, max=75), val.input_required()],
        description='maxclusters',
        default=50,
        render_kw={
            'class': 'short',
            'step': 1
        }
    )

class ClinkerAlignmentForm(Form):
    noAlign = BooleanField(
        label=u'Don\'t align clusters',
        validators=[], # TODO: add boolean validators,
        description='noAlign'
    )

    identity = DecimalField(
        label=u'Min. alignment sequence identity',
        validators=[is_safe_string_value, val.input_required(), val.number_range(min=0, max=1)],
        description='identity',
        default=0.30,  # for some reason, default is not working here
        render_kw={
            'step': 0.01,
        }
    )

class ClinkerInputForm(Form):
    fileUploadClinker = MultipleFileField(
        label=u'Genome files*',
        validators=[val.optional()],  # TODO: safe filename
        description='fileUploadClinker',
        render_kw={
            'accept': ','.join(genbank_extensions),
            'onchange': 'getGenBankFileNames()',
            'required': ''
        }
    )

class ClinkerOutputForm(Form):
    clinkerDelim = StringField(
        label=u'Delimiter',
        validators=[val.length(max=1), val.Optional(), is_safe_string_value],
        description='generalDelimiter',
        render_kw={
            'size': 1,
            'class': 'short'
        }
    )

    clinkerDecimals = IntegerField(
        label=u'Decimals',
        validators=[val.input_required(), is_safe_string_value, val.number_range(min=0, max=9)],
        description='generalDecimals',
        default=2,
        render_kw={
            'step': 1,
            'class': 'short'
        }
    )

    hideLinkHeaders = BooleanField(
        label=u'Hide alignment column headers',
        validators=[], # TODO: add boolean validators,
        description='hideLinkHeaders'
    )

    hideAlignHeaders = BooleanField(
        label=u'Hide alignment cluster name headers',
        validators=[], # TODO: add boolean validators,
        description='hideAlignHeaders'
    )

class ClinkerAdditionalOptionsForm(Form):
    useFileOrder = BooleanField(
        label=u'Maintain order of input files',
        validators=[], # TODO: add boolean validators,
        description='hideAlignHeaders'
    )
