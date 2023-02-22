
Developer Installation
======================

To start, create a virtual enviroment. For example::

    conda create -n pdpilot
    conda activate pdpilot
    conda install python nodejs yarn jupyterlab

Next, clone the repository::

    git clone https://github.com/DanielKerrigan/PDPilot
    cd PDPilot

Next, install the package::

    pip install -e ".[examples,docs,dev,test]"

If you are using classic Jupyter notebook, then enable the extention with these commands::

    jupyter nbextension install --sys-prefix --symlink --overwrite --py pdpilot
    jupyter nbextension enable --sys-prefix --py pdpilot

If you are using Jupyter Lab, then run::

    jupyter labextension develop --overwrite .

In one terminal, watch for JS changes::

    yarn watch

In another terminal, run Jupyter notebook or lab::

    jupyter notebook

After making JS changes, refresh your browser window. After making Python changes, restart the kernel.
