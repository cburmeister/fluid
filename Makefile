.PHONY: init clean clean_js clean_tmp clean_pyc

init:
	pip install -r requirements.txt

clean: clean_js clean_tmp clean_pyc

clean_js:
	rm -rf app/bower_components

clean_tmp:
	find app/static/tmp -name '*.jpg' -delete
	find app/static/tmp -name '*.json' -delete

clean_pyc:
	find . -name '*.pyc' -delete
