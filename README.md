# pdp-explorer

This repository contains a Jupyter widget and a Python library for exploring partial dependence plots.

![Screenshot](screenshot.png?raw=true)

## Installation

The easiest way to try out the widget is to install it in a conda environment and use that environment both for the kernel and to run `jupyter notebook` or `jupyter lab`. For example:

```bash
# Create a conda environment.
conda create -n pdpexplorer
conda activate pdpexplorer
conda install nodejs yarn jupyterlab

# Install the package.
# Run this from the pdp-explorer directory.
pip install -e .

# Run the examples.
cd examples
jupyter notebook
```

If your kernel is in a separate environment from where you run `jupyter notebook` or `jupyter lab`, then you will need to install the widget in both environments. If you are using JupyterHub, then you will need to refresh the page in your browser after installing the package.
