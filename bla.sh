#!/bin/bash

for file in ./data/correct_names/*.txt
do
  i=${file:27}
  i=${i%.txt}
  echo File $i.html
  python tokenizer.py data/correct_names/names_$i.txt downloaded_pages/faculty/$i.html >> bli.txt
done
