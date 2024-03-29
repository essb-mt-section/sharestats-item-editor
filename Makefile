.PHONY: install clean build

build:
		python3 setup.py sdist bdist_wheel

publish_test:
	twine check dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish:
	twine check dist/*
	twine upload dist/*

setup_venv:
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt

clean:
	py3clean .
	rm -rf build dist  *.egg-info

meld:
	meld ../rexam-item-editor/rexam_item_editor sharestats_item_editor/rexam_item_editor/

