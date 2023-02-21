
pdp-explorer
=====================================

.. image:: screenshots/overview.png
   :width: 800
   :alt: A screenshot of the "One-way Plots" tab of the tool's user interface.

pdp-explorer is a Jupyter widget for exploring partial dependence plots (PDPs) and individual conditional expectation (ICE) plots. You can find the code on `GitHub <https://github.com/nyuvis/pdp-ranking>`_.

.. .. admonition:: User Study

..    We are conducting a user study to evaluate how machine learning (ML) practitioners use pdp-explorer to analyze the behavior of a ML model. We are looking for ML practitioners who have experience using PDP or ICE plots to participate. The study will be conducted over video call and will take approximately one hour. Participants will be instructed how to use the tool, will analyze a model, and will then complete a brief interview. Participants will be compensated with a $30 Amazon gift card. If you are interested in participating, please fill out this `form <https://forms.gle/tL6NoUZtYsSdCEsx9>`_.
   
..    This work is research collaboration between the Khoury College of Computer Sciences at Northeastern University and Capital One.  For any questions, please reach out to Daniel Kerrigan at kerrigan.d@northeastern.edu.

Quickstart
----------

To get started, install with pip::

    pip install pdpexplorer

Or, you can try the widget in this `Colab notebook <https://colab.research.google.com/github/nyuvis/pdp-ranking/blob/main/examples/colab-example.ipynb>`_.

See the `example notebooks <https://github.com/nyuvis/pdp-ranking/tree/main/examples>`_ for more demonstrations.

.. toctree::
   :caption: User Guide

   usage
   api

.. toctree::
   :caption: Developer Guide

   developer-installation
   release
