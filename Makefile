.PHONY: init clean

init:
	pip install -r requirements.txt

clean:
	find . -name '*.pyc' -delete
	find app/static/tmp -name '*.jpg' -delete
	find app/static/tmp -name '*.json' -delete
