#!/usr/bin/env python
# coding: utf-8

"""
Add module docstring for pdpexplorer
"""

from .logging import mylog

import json
from pathlib import Path
from typing import Callable, Union, List

from ipywidgets import DOMWidget
from traitlets import Dict, Int, List as ListTraitlet, Unicode, observe
import pandas as pd

from pdpexplorer.pdp import calc_two_way_pd, get_feature_to_pd

from ._frontend import module_name, module_version


class PDPExplorerWidget(DOMWidget):
    """This class creates the interactive widget.

    :param predict: A function whose input is a DataFrame of instances and
        returns the model's predictions on those instances.
    :type predict: Callable[[pd.DataFrame], list[float]]
    :param df: Instances to use to compute the PDPs and ICE plots.
    :type df: pd.DataFrame
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

    feature_names = ListTraitlet([]).tag(sync=True)
    feature_info = Dict({}).tag(sync=True)

    dataset = Dict({}).tag(sync=True)

    num_instances = Int(0).tag(sync=True)

    one_way_pds = ListTraitlet([]).tag(sync=True)
    two_way_pds = ListTraitlet([]).tag(sync=True)

    two_way_pdp_extent = ListTraitlet([0, 0]).tag(sync=True)
    two_way_interaction_extent = ListTraitlet([0, 0]).tag(sync=True)

    ice_line_extent = ListTraitlet([0, 0]).tag(sync=True)
    ice_cluster_center_extent = ListTraitlet([0, 0]).tag(sync=True)
    ice_cluster_band_extent = ListTraitlet([0, 0]).tag(sync=True)
    ice_cluster_line_extent = ListTraitlet([0, 0]).tag(sync=True)

    height = Int(600).tag(sync=True)

    highlighted_indices = ListTraitlet([]).tag(sync=True)

    two_way_to_calculate = ListTraitlet([]).tag(sync=True)

    def __init__(
        self,
        predict: Callable[[pd.DataFrame], List[float]],
        df: pd.DataFrame,
        pd_data: Union[str, Path, dict],
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

        # synced widget state

        self.feature_names = sorted([p["x_feature"] for p in pd_data["one_way_pds"]])
        self.feature_info = pd_data["feature_info"]

        self.dataset = pd_data["dataset"]

        self.num_instances = pd_data["num_instances"]

        self.one_way_pds = pd_data["one_way_pds"]
        self.two_way_pds = pd_data["two_way_pds"]

        self.two_way_pdp_extent = pd_data["two_way_pdp_extent"]
        self.two_way_interaction_extent = pd_data["two_way_interaction_extent"]

        self.ice_line_extent = pd_data["ice_line_extent"]
        self.ice_cluster_center_extent = pd_data["ice_cluster_center_extent"]
        self.ice_cluster_band_extent = pd_data["ice_cluster_band_extent"]
        self.ice_cluster_line_extent = pd_data["ice_cluster_line_extent"]

        self.height = height

        # not synced
        self.df = df
        self.predict = predict
        self.feature_to_pd = get_feature_to_pd(self.one_way_pds)

    @observe("two_way_to_calculate")
    def _on_two_way_to_calculate_change(self, change):
        pair = change["new"]

        if len(pair) != 2:
            return

        for pdp in self.two_way_pds:
            if (pdp["x_feature"] == pair[0] and pdp["y_feature"] == pair[1]) or (
                pdp["x_feature"] == pair[1] and pdp["y_feature"] == pair[0]
            ):
                return

        result = calc_two_way_pd(
            self.predict,
            self.df.copy(),
            self.df.copy(),
            pair,
            self.feature_info,
            self.feature_to_pd,
        )

        # update the extents

        self.two_way_pdp_extent = [
            min(self.two_way_pdp_extent[0], result["pdp_min"]),
            max(self.two_way_pdp_extent[1], result["pdp_max"]),
        ]

        if result["interaction_min"] < self.two_way_interaction_extent[0]:
            self.two_way_interaction_extent = [
                result["interaction_min"],
                result["interaction_max"],
            ]

        two_ways = self.two_way_pds.copy()
        two_ways.append(result)
        self.two_way_pds = two_ways
