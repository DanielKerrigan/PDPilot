
Release Process
===============

#. Update the versions in ``package.json``, ``pdpexplorer/_version.py``, and ``docs/conf.py``.
#. Make a release commmit: ``git commit -m "release vX.Y.Z"``
#. Tag the commit: ``git tag vX.Y.Z``
#. Push the commit and tag: ``git push && git push --tags``
#. Bundle the Python package: ``python setup.py sdist bdist_wheel``
#. Install twine: ``pip install twine``
#. Publish the package to PyPI: ``twine upload dist/pdpexplorer*``
