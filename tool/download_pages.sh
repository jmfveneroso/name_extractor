#!/bin/bash

i=218
while read p; do
  curl $p > downloaded_pages/faculty/$i.html
  echo "downloaded downloaded_pages/faculty/$i.html"
  ((i = i + 1))
done < the_faculties.txt
