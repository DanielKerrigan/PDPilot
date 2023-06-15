
Installation
============

The :code:`pdpilot` package is available on `PyPI <https://pypi.org/project/pdpilot/>`_ and can be installed with pip. When working with virtual environments, it is easiest to run the Jupyter server and kernel in the same environment.

Here's an example of using conda and JupyterLab::

    # Set up the environment.
    conda create -n pdpilot
    conda activate pdpilot
    # Install Python and JupyterLab.
    conda install -c conda-forge "python=3.10" jupyterlab
    # Install PDPilot.
    pip install pdpilot
    # Run the server.
    jupyter-lab

And here's an example of using conda and Jupyter Notebook::

    # Set up the environment.
    conda create -n pdpilot
    conda activate pdpilot
    # Install Python and Jupyter Notebook.
    conda install -c conda-forge "python=3.10" notebook
    # Install PDPilot.
    pip install pdpilot
    # Run the server.
    jupyter-notebook

With Jupyter Notebook, if you see errors in your terminal such as "Uncaught exception in zmqstream callback" or "zmq message arrived on closed channel", then it is related to this `open issue <https://github.com/jupyter/notebook/issues/6721>`_. To avoid this error, you can update the :code:`conda install` command to :code:`conda install -c conda-forge "python=3.10" "pyzmq<25" "jupyter_client<8" notebook`.

To get you started, you can download an `example notebook <https://github.com/DanielKerrigan/PDPilot/blob/main/examples/bike-rentals-regression.ipynb>`_::
    
    curl -O https://raw.githubusercontent.com/DanielKerrigan/PDPilot/main/examples/bike-rentals-regression.ipynb
