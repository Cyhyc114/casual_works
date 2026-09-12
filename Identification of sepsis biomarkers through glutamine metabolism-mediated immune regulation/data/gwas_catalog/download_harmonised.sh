#!/bin/bash

declare -A ranges
ranges[GCST90001917]="GCST90001001-GCST90002000"
ranges[GCST90001592]="GCST90001001-GCST90002000"
ranges[GCST90001411]="GCST90001001-GCST90002000"
ranges[GCST90002072]="GCST90002001-GCST90003000"
ranges[GCST90002077]="GCST90002001-GCST90003000"

for gcst in GCST90001917 GCST90001592 GCST90001411 GCST90002072 GCST90002077; do
  range="${ranges[$gcst]}"
  url="https://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/${range}/${gcst}/harmonised/32929287-${gcst}-EFO_0007937.h.tsv.gz"
  echo "Downloading ${gcst} ..."
  
  aria2c \
    -x 16 \
    -s 16 \
    -k 1M \
    -c \
    --retry-wait=3 \
    --max-tries=0 \
    --timeout=60 \
    --file-allocation=none \
    -o "${gcst}.h.tsv.gz" \
    "$url"
done