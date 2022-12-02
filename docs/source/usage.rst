
Usage
=====

To start, create a virtual enviroment. For example::

    conda create -n pdpexplorer
    conda activate pdpexplorer
    conda install python nodejs yarn jupyterlab

Next, clone the repository::

    git clone https://github.com/nyuvis/pdp-ranking
    cd pdp-ranking

Next, install the package::

    pip install -e ".[examples,docs,dev,test]"

If you are using classic Jupyter notebook, then enable the extention with these commands::

    jupyter nbextension install --sys-prefix --symlink --overwrite --py pdpexplorer
    jupyter nbextension enable --sys-prefix --py pdpexplorer

If you are using Jupyter Lab, then run::

    jupyter labextension develop --overwrite .

In one terminal, watch for JS changes::

    yarn watch

In another terminal, run Jupyter notebook or lab::

    jupyter notebook

After making JS changes, refresh your browser window. After making Python changes, restart the kernel.
