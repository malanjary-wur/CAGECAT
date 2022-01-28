#!/bin/bash
# Author: Matthias van den Belt

# TODO future: find out how we can obtain the families of organisms from NCBI
# TODO future: we could also adapt this script to download fungi genomes

if test "$#" -ne 1; then
    echo "No organism entered"
    exit 1
fi

if [ "$1" == 'prokaryota' ]; then
  echo "Using RefSeqs"
  ftp_labels="FtpPath_RefSeq"
elif [ "$1" == 'fungi' ]; then
    echo "Using GenBanks + Refseqs"
    ftp_labels="FtpPath_GenBank FtpPath_RefSeq"
else
  echo "Invalid organism provided"

  exit 1
fi

echo "Constructing HMM databases for organism: $1"

fn_non_unique="non_unique_genera.txt"
fn_unique="unique_genera.txt"

echo "If you try to rerun this script, make sure to remove any unmoved files.."
echo ".. from the default RefSeq GBKS storage folder to prevent missing a file"

echo "Removing too_few_species.txt"
rm too_few_species.txt

echo " Fetching all genera from NCBI"
esearch -db assembly -query '((('"$1"'[orgn] AND ("representative genome"[refseq category] OR "reference genome"[refseq category])) AND (latest[filter] AND all[filter] NOT anomalous[filter])))' | efetch -format docsum | xtract -pattern DocumentSummary -element Organism > "$fn_non_unique"

echo " Creating list of unique genera"
total_genera=$(python3 get_unique_genera.py "${fn_non_unique}" "${fn_unique}")

i=0
echo " Downloading genomes"
for genus in $(cat "$fn_unique")
do
  i=$((i+1))

  echo " Processing ${genus} (${i} of ${total_genera})"
  echo "   -> Fetching FTP paths"
#  echo "esearch -db assembly -query '((('$1'[orgn] AND ('representative genome'[refseq category] OR 'reference genome'[refseq category])) AND (latest[filter] AND all[filter] NOT anomalous[filter]))) AND '${genus}'[Organism]' | efetch -format docsum | xtract -pattern DocumentSummary -element {$ftp_labels} SpeciesName > ${genus}_ftp_paths.txt"
#  echo "${ftp_labels}"
#  echo "$ftp_labels"
#  echo $ftp_labels
#  echo ${ftp_labels}
#  echo "--"

  esearch -db assembly -query '((('"$1"'[orgn] AND ("representative genome"[refseq category] OR "reference genome"[refseq category])) AND (latest[filter] AND all[filter] NOT anomalous[filter]))) AND '${genus}'[Organism]' | efetch -format docsum | xtract -pattern DocumentSummary -element $ftp_labels SpeciesName > "${genus}_ftp_paths.txt"

  echo "   -> Downloading files"
  python3 download_files.py "${genus}_ftp_paths.txt" "$1"
done

echo "Creating file to stop creating databases"
python3 download_files.py 'everything_has_been_downloaded'

echo "Removing ftp paths files"
rm *_ftp_paths.txt

echo "Done!"
