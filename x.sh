#!/bin/bash

while read p; do
  ./test_faculty.sh $p
done < nums
