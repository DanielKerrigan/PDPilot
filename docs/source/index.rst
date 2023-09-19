
PDPilot
=======

.. image:: https://github.com/DanielKerrigan/PDPilotExtras/blob/main/pdpilot-overview.gif?raw=true
   :width: 800
   :alt: An animated GIF providing an overview of PDPilot.

PDPilot is a Jupyter widget for exploring partial dependence plots (`PDPs <https://christophm.github.io/interpretable-ml-book/pdp.html>`_) and individual conditional expectation (`ICE <https://christophm.github.io/interpretable-ml-book/ice.html>`_) plots. You can find the code on `GitHub <https://github.com/DanielKerrigan/PDPilot>`_.

.. admonition:: User Study

   We are conducting a user study to evaluate how machine learning (ML) practitioners use PDPilot to analyze the behavior of an ML model. We are looking for ML practitioners who have experience using PDP or ICE plots to participate. The study will be conducted over a recorded video call and will take approximately two hours. Participants will be instructed how to use the tool, will analyze a model, and will then complete a brief interview. Participants will be compensated with a $100 virtual Amazon gift card. We anticipate that the study will take place during June and July. You must be at least 18 years old to participate. If you are interested in participating, please fill out this `form <https://forms.gle/JjFb3qcVWj7dk7cq8>`_.
   
   This study has been reviewed and approved by Northeastern University IRB. It is being conducted by Daniel Kerrigan and Enrico Bertini at the Khoury College of Computer Sciences at Northeastern University. For any questions, please reach out to Daniel at kerrigan.d@northeastern.edu.

Quickstart
----------

You can try the widget in your browser with this `Colab notebook <https://colab.research.google.com/github/DanielKerrigan/PDPilot/blob/main/examples/colab-example.ipynb>`_.

To get started locally, install with pip::

    pip install pdpilot

See the `example notebooks <https://github.com/DanielKerrigan/PDPilot/tree/main/examples>`_ for demonstrations.

.. toctree::
   :caption: User Guide

   installation
   api
   ui

.. toctree::
   :caption: Developer Guide

   developer-installation
   release
