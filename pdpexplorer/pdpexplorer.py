#!/usr/bin/env python
# coding: utf-8

"""
TODO: Add module docstring for pdpexplorer
"""

import json
from pathlib import Path

from ipywidgets import DOMWidget
from traitlets import Dict, Int, List, Unicode

from ._frontend import module_name, module_version


class PDPExplorerWidget(DOMWidget):
    """This class creates the interactive widget.

    :param pd_data: The dictionary returned by :func:`pdpexplorer.pdp.partial_dependence`
        or a path to the file containing that data.
    :type pd_data: dict | str | Path
    :param height: The height of the widget in pixels, defaults to 600.
    :type height: int, optional
    :raises OSError: Raised if ``pd_data`` is a str or Path and the file cannot be read.
    """

    _model_name = Unicode("PDPExplorerModel").tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode("PDPExplorerView").tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    # widget state that is synced between backend and frontend

    feature_names = List([]).tag(sync=True)
    feature_info = Dict({}).tag(sync=True)

    dataset = Dict({}).tag(sync=True)

    num_instances = Int(0).tag(sync=True)

    one_way_pds = List([]).tag(sync=True)
    two_way_pds = List([]).tag(sync=True)

    pdp_extent = List([0, 0]).tag(sync=True)
    ice_mean_extent = List([0, 0]).tag(sync=True)
    ice_band_extent = List([0, 0]).tag(sync=True)
    ice_line_extent = List([0, 0]).tag(sync=True)

    one_way_quantitative_clusters = List([]).tag(sync=True)
    one_way_categorical_clusters = List([]).tag(sync=True)

    height = Int(600).tag(sync=True)

    def __init__(
        self,
        pd_data: str | Path | dict,
        height: int = 600,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # if pd_data is a path or string, then read the file at that path
        if isinstance(pd_data, Path) or isinstance(pd_data, str):
            path = Path(pd_data).resolve()

            if not path.exists():
                raise OSError(f"Cannot read {path}")

            json_data = path.read_text(encoding="utf-8")
            pd_data = json.loads(json_data)

        self.feature_names = sorted([p["x_feature"] for p in pd_data["one_way_pds"]])
        self.feature_info = pd_data["feature_info"]

        self.dataset = pd_data["dataset"]

        self.num_instances = pd_data["num_instances"]

        self.one_way_pds = pd_data["one_way_pds"]
        self.two_way_pds = pd_data["two_way_pds"]

        self.pdp_extent = pd_data["pdp_extent"]
        self.ice_mean_extent = pd_data["ice_mean_extent"]
        self.ice_band_extent = pd_data["ice_band_extent"]
        self.ice_line_extent = pd_data["ice_line_extent"]

        self.one_way_quantitative_clusters = pd_data["one_way_quantitative_clusters"]
        self.one_way_categorical_clusters = pd_data["one_way_categorical_clusters"]

        self.height = height
