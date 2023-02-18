# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information

project = "pdpexplorer"
copyright = "2023, Daniel Kerrigan"
author = "Daniel Kerrigan"

# get version from python package:
import os

here = os.path.dirname(__file__)
repo = os.path.join(here, "..", "..")
_version_py = os.path.join(repo, "pdpexplorer", "_version.py")
version_ns = {}
with open(_version_py) as f:
    exec(f.read(), version_ns)

# The short X.Y version.
version = "%i.%i" % version_ns["version_info"][:2]
# The full version, including alpha/beta/rc tags.
release = version_ns["__version__"]

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "furo"

# -- Options for EPUB output
epub_show_urls = "footnote"
