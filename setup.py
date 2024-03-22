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
    skip_if_exists,
)

HERE = os.path.dirname(os.path.abspath(__file__))


# The name of the project
name = "pdpilot"

# Get the version
version = get_version(pjoin(name, "_version.py"))


# Representative files that should exist after a successful build
jstargets = [
    pjoin(HERE, name, "nbextension", "index.js"),
    pjoin(HERE, name, "labextension", "package.json"),
]


package_data_spec = {name: ["nbextension/**js*", "labextension/**"]}


data_files_spec = [
    ("share/jupyter/nbextensions/pdpilot", "pdpilot/nbextension", "**"),
    ("share/jupyter/labextensions/pdpilot", "pdpilot/labextension", "**"),
    ("share/jupyter/labextensions/pdpilot", ".", "install.json"),
    ("etc/jupyter/nbconfig/notebook.d", ".", "pdpilot.json"),
]


cmdclass = create_cmdclass(
    "jsdeps", package_data_spec=package_data_spec, data_files_spec=data_files_spec
)
npm_install = combine_commands(
    install_npm(HERE, build_cmd="build:prod"),
    ensure_targets(jstargets),
)

cmdclass["jsdeps"] = skip_if_exists(jstargets, npm_install)

setup_args = dict(
    name=name,
    description="A Jupyter widget for exploring PDP and ICE plots.",
    version=version,
    scripts=glob(pjoin("scripts", "*")),
    cmdclass=cmdclass,
    packages=find_packages(),
    author="Daniel Kerrigan",
    author_email="kerrigan.d@northeastern.edu",
    url="https://github.com/DanielKerrigan/PDPilot",
    license="BSD",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "Widgets", "IPython", "PDP", "ICE"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Jupyter",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    include_package_data=True,
    python_requires=">=3.7.1",
    install_requires=[
        "ipywidgets>=7.6.0,<9",
        "pandas>=1.3.5",
        "numpy>=1.21.5",
        "joblib>=1.1.0",
        "scikit-learn>=1.0.2",
        "tqdm>=4.64.1",
    ],
    extras_require={
        "examples": ["pmlb", "xgboost"],
        "docs": ["sphinx", "furo"],
        "dev": ["twine", "jupyter_packaging"],
        "test": ["pytest"],
    },
    entry_points={},
)

if __name__ == "__main__":
    setup(**setup_args)
