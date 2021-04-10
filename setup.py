#!/usr/bin/env python3
"""
Installer
"""

from setuptools import setup
import codecs
import os
from sys import version_info as _vi

package_name = "sharestats_item_editor"
application_name = "sharestats-item-editor"

install_requires = ["appdirs>=1.4",
                    "pysimplegui>=4.33"]

extras_require = {
}

entry_points = {'console_scripts':
                ['{}={}.__main__:run'.format(application_name, package_name)]}

packages = [package_name]
for subp in ["templates"]:
    packages.append("{}.{}".format(package_name, subp))


if _vi.major< 1:
    raise RuntimeError("{0} requires Python 3 or larger.".format(application_name))

def readme():
    directory = os.path.dirname(os.path.join(
        os.getcwd(), __file__, ))
    with codecs.open(
        os.path.join(directory, "README.md"),
        encoding="utf8",
        mode="r",
        errors="replace",
        ) as file:
        return file.read()

def get_version(package):
    """Get version number"""

    with open(os.path.join(package, "__init__.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("'")[1]
    return "None"


if __name__ == '__main__':
    setup(
        name = application_name,
        version=get_version(package_name),
        description='Editor and validator for Rexam items in the ShareStats '
                    'project',
        author='Oliver Lindemann',
        author_email='lindemann@cognitive-psychology.eu',
        license='GNU GPLv3',
        url='https://github.com/essb-mt-section/sharestats-item-editor/',
        packages=packages,
        include_package_data=True,
        setup_requires=[],
        install_requires=install_requires,
        entry_points=entry_points,
        extras_require=extras_require,
        keywords = "", #ToDo
        classifiers=[
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Topic :: Scientific/Engineering"
        ],
        long_description=readme(),
        long_description_content_type='text/markdown'
    )