#!/bin/bash

for file in ./data/correct_names/*.txt
do
  i=${file:27:(-4)}
  echo File $i.html
  python name_extractor.py downloaded_pages/faculty/$i.html | python comparator.py data/correct_names/names_$i.txt
done
