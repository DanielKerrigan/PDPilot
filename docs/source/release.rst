
Release Process
===============

1. Update the versions in ``package.json``, ``pdpexplorer/_version.py``, and ``docs/conf.py``.
2. Bundle the Python package: ``python setup.py sdist bdist_wheel``
3. Install twine: ``pip install twine``
4. Publish the package to PyPI: ``twine upload dist/pdpexplorer*``
5. Tag the last commit: ``git tag vx.y.z``
6. Push the tag: ``git push --tags``