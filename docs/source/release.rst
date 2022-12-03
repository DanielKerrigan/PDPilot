
Release Process
===============

1. Update the versions in ``package.json``, ``pdpexplorer/_version.py``, and ``docs/conf.py``.
2. Make a release commmit: ``git commit -m "release vX.Y.Z"``
3. Tag the commit: ``git tag vX.Y.Z``
4. Push the commit and tag: ``git push && git push --tags``
6. Bundle the Python package: ``python setup.py sdist bdist_wheel``
7. Install twine: ``pip install twine``
8. Publish the package to PyPI: ``twine upload dist/pdpexplorer*``
