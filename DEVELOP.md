# pdp-explorer

A Jupyter widget and Python library for exploring partial dependence plots.

## Development Installation

Create a dev environment:

```bash
conda create -n pdpexplorer
conda activate pdpexplorer
conda install nodejs yarn jupyterlab
```

Install the Python package and build the TypeScript package.

```bash
pip install -e '.[examples]'
```

When developing your extensions, you need to manually enable your extensions with the
notebook / lab frontend. For lab, this is done by the command:

```
jupyter labextension develop --overwrite .
yarn run build
```

For classic notebook, you need to run:

```
jupyter nbextension install --sys-prefix --symlink --overwrite --py pdpexplorer
jupyter nbextension enable --sys-prefix --py pdpexplorer
```

Note that the `--symlink` flag doesn't work on Windows, so you will here have to run
the `install` command every time that you rebuild your extension. For certain installations
you might also need another flag instead of `--sys-prefix`, but we won't cover the meaning
of those flags here.

### How to see your changes
### Jupyter Notebook:
For Jupyter Notebook you can just watch for JS changes:

```bash
yarn watch
```

#### Jupyter Lab:
If you use JupyterLab to develop then you can watch the source directory and run JupyterLab at the same time in different
terminals to watch for changes in the extension's source and automatically rebuild the widget.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
yarn watch
# Watch to rebuild JupyterLab
jupyter labextension watch
# Run JupyterLab in another terminal
jupyter lab
```

After a change wait for the build to finish and then refresh your browser and the changes should take effect.

#### Python:
If you make a change to the python code then you will need to restart the notebook kernel to have it take effect.
