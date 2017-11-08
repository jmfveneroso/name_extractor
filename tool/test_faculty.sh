#!/bin/bash

if [ $# -eq 0 ]; then
  for file in ./data/correct_names/*.txt
  do
    i=${file:27}
    i=${i%.txt}
    echo File $i.html
    python name_extractor.py downloaded_pages/faculty/$i.html | python comparator.py data/correct_names/names_$i.txt
  done
else
  python name_extractor.py downloaded_pages/faculty/$1.html | python comparator.py data/correct_names/names_$1.txt -v
fi
