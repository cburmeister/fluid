.PHONY: init clean

init:
	pip install -r requirements.txt

clean:
	find . -name '*.pyc' -delete
	find static/tmp -name '*.jpg' -delete
	find static/tmp -name '*.json' -delete
