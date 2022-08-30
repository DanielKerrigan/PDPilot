#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from glob import glob
import os
from os.path import join as pjoin
from setuptools import setup, find_packages


from jupyter_packaging import (
    create_cmdclass,
    install_npm,
    ensure_targets,
    combine_commands,
    get_version,
)

HERE = os.path.dirname(os.path.abspath(__file__))


# The name of the project
name = "pdpexplorer"

# Get the version
version = get_version(pjoin(name, "_version.py"))


# Representative files that should exist after a successful build
jstargets = [
    pjoin(HERE, name, "nbextension", "index.js"),
    pjoin(HERE, "lib", "index.js"),
]


package_data_spec = {name: ["nbextension/**js*", "labextension/**"]}


data_files_spec = [
    ("share/jupyter/nbextensions/pdpexplorer", "pdpexplorer/nbextension", "**"),
    ("share/jupyter/labextensions/pdp-explorer", "pdpexplorer/labextension", "**"),
    ("share/jupyter/labextensions/pdp-explorer", ".", "install.json"),
    ("etc/jupyter/nbconfig/notebook.d", ".", "pdpexplorer.json"),
]


cmdclass = create_cmdclass(
    "jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec
)
cmdclass["jsdeps"] = combine_commands(
    install_npm(HERE, build_cmd="build:prod"),
    ensure_targets(jstargets),
)


setup_args = dict(
    name=name,
    description="A Jupyter widget for exploring partial dependence plots.",
    version=version,
    scripts=glob(pjoin("scripts", "*")),
    cmdclass=cmdclass,
    packages=find_packages(),
    author="Daniel Kerrigan",
    author_email="kerrigan.d@northeastern.edu",
    url="https://github.com/nyuvis/pdp-explorer",
    license="BSD",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "Widgets", "IPython"],
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: Jupyter",
    ],
    include_package_data=True,
    python_requires=">=3.7.1",
    install_requires=[
        "ipywidgets>=7.6.0",
        "pandas>=1.3.5",
        "numpy>=1.21.5",
        "plotnine>=0.8.0",
        "joblib>=1.1.0",
        "scikit-learn>=1.0.2",
        "tslearn>=0.5.2",
    ],
    extras_require={
        "examples": [],
        "dev": ["pylint", "black"],
        "test": ["pytest"],
    },
    entry_points={},
)

if __name__ == "__main__":
    setup(**setup_args)
