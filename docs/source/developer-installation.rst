
Developer Installation
======================

To start, create a virtual enviroment. For example::

    conda create -n pdpilot
    conda activate pdpilot
    conda install -c conda-forge "python=3.8" nodejs jupyterlab notebook "jupyter_client<8" "pyzmq<25"

The inclusion of :code:`jupyter_client<8` and :code:`pyzmq<25` is needed until this `issue <https://github.com/jupyter/notebook/issues/6721>`_ is resolved.

Next, clone the repository::

    git clone https://github.com/DanielKerrigan/PDPilot
    cd PDPilot

Next, install the package::

    pip install -e ".[examples,docs,dev,test]"

Jupyter Notebook
----------------

If you are using classic Jupyter notebook, then enable the extention with these commands::

    jupyter nbextension install --sys-prefix --symlink --overwrite --py pdpilot
    jupyter nbextension enable --sys-prefix --py pdpilot

In one terminal, watch for JS changes::

    npm run watch

In another terminal, run Jupyter::

    jupyter notebook

After making JS changes, refresh your browser window. After making Python changes, restart the kernel.

Jupyter Lab
-----------

If you are using Jupyter Lab, then run::

    jupyter labextension develop --overwrite .

Then run Jupyter::

    jupyter lab

After making JS changes, run::

    npm run build

After making Python changes, restart the kernel.
