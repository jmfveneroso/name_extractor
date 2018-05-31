# Name Extractor

This repository contains the results of an ongoing research on Web Information Extraction, and, more precisely, Researcher Name Extraction from faculty directories.

The partial results for this information extraction model have been described in a poster published on the [Joint Conference on Digital Libraries 2018](https://2018.jcdl.org/). The poster can be read [here](https://github.com/jmfveneroso/name_extractor/blob/master/tex/poster/poster.pdf). For more information, the full paper can be read [here](https://github.com/jmfveneroso/name_extractor/blob/master/tex/example.pdf).

This repository has been modified considerably since the original poster was published. The JCDL 2018 results were produced with the version from commit 
13e5949868adce3ee942c798b7628b7ea6b89559. 

The current version was made cleaner to be more easily comprehended, but, in time it will be upgraded with all the features from the old version.

## Extractors

This module implements 4 name extractors:

* Exact matching extractor
* NLTK extractor
* Naive Bayesian extractor
* Not-so-naive Bayesian (NSNB) extractor (the model described in the poster)

## Dataset

This repository contains a dataset of 149 faculty pages inside the "dataset" directory. The directory also contains the target names for each page.


## Running the code

First install the required packages with:
```
make init
```

To run the 5 fold cross validation test with all 149 pages for the NSNB extractor, execute:
```
make run
```
It wil print the **precision** and **recall** for each test fold.

---

To extract names from a faculty page and print them, run:

```
make extract URL=${URL}
```
*It may take a few seconds to load the probabilities.*

Just to start, you can try:
```
make extract URL=https://www.sice.indiana.edu/all-people/index.html
make extract URL=http://www.dcc.ufmg.br/dcc/?q=pt-br/professores
```

## Contact

If you have any question send an email to **jmfveneroso@gmail.com**.
