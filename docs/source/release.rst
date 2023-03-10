
Release Process
===============

#. Update the versions in ``package.json``, ``pdpilot/_version.py``, and ``pdpilot/_frontend.py``.
#. Make a release commmit: ``git add . && git commit -m "release vX.Y.Z"``
#. Tag the commit: ``git tag vX.Y.Z``
#. Push the commit and tag: ``git push && git push --tags``
#. Release the npm packages: ``npm login`` and ``npm publish``
#. Bundle the Python package: ``python setup.py sdist bdist_wheel``
#. Publish the package to PyPI: ``twine upload dist/pdpilot-X.Y.Z*``
