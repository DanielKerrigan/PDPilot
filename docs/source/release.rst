
Release Process
===============

#. Update the versions in ``package.json``, ``pdpexplorer/_version.py``, and ``pdpexplorer/_frontend.py``.
#. Update documentation and run ``make html``.
#. Make a release commmit: ``git commit -m "release vX.Y.Z"``
#. Tag the commit: ``git tag vX.Y.Z``
#. Push the commit and tag: ``git push && git push --tags``
#. Release the npm packages: ``npm login`` and ``npm publish``
#. Bundle the Python package: ``python setup.py sdist bdist_wheel``
#. Publish the package to PyPI: ``twine upload dist/pdpexplorer-X.Y.Z*``
