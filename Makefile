.PHONY: install clean build

build:
	python3 setup.py sdist bdist_wheel

publish:
	twine check dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

setup_venv:
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt

clean:
	@rm -rf build \
        dist\
        *.egg-info \
