init:
	pip install -r requirements.txt

run:
	python name_extractor/tester.py

extract:
	python name_extractor/nsnb_extractor.py $(URL)
