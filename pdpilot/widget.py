#!/usr/bin/env python
# coding: utf-8

"""
PDPilot widget module.
"""

import copy
import json
import math
from pathlib import Path
from typing import Callable, List, Union

import numpy as np
import pandas as pd
from ipywidgets import DOMWidget
from numpy.random import MT19937, RandomState, SeedSequence
from traitlets import Dict, Int
from traitlets import List as ListTraitlet
from traitlets import Unicode, observe

from pdpilot._frontend import module_name, module_version
from pdpilot.pdp import _calc_two_way_pd, _get_clusters_info, _get_feature_to_pd
from pdpilot.utils import convert_keys_to_ints


class PDPilotWidget(DOMWidget):
    """This class creates the interactive widget.

    :param predict: A function whose input is a DataFrame of instances and
        returns the model's predictions on those instances.
    :type predict: Callable[[pd.DataFrame], list[float]]
    :param df: Instances to use to compute the PDPs and ICE plots.
    :type df: pd.DataFrame
    :param labels: Ground truth labels for the instances in ``df``.
    :type labels: list[float] | list[int] | np.ndarray | pd.Series
    :param pd_data: The dictionary returned by :func:`pdpilot.pdp.partial_dependence`
        or a path to the file containing that data.
    :type pd_data: dict | str | Path
    :param seed:  Random state for clustering. Defaults to None.
    :type seed: int | None, optional
    :param height: The height of the widget in pixels, defaults to 600.
    :type height: int, optional
    :raises OSError: Raised if ``pd_data`` is a str or Path and the file cannot be read.
    """

    _model_name = Unicode("PDPilotModel").tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode("PDPilotView").tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    # widget state that is synced between backend and frontend

    feature_names = ListTraitlet([]).tag(sync=True)
    feature_info = Dict({}).tag(sync=True)

    dataset = Dict({}).tag(sync=True)

    labels = ListTraitlet([]).tag(sync=True)

    num_instances = Int(0).tag(sync=True)

    one_way_pds = ListTraitlet([]).tag(sync=True)
    """
    The ice lines are a lot of data, so we want to limit how often we have to
    transfer them between the backend and frontend. If they were a part of
    one_way_pds, then they would get sent whenever the ICE clusters get
    adjusted in the detailed plot view. By separating them out, adjusting
    the clusters becomes faster and won't run into the "message too big"
    errors with tornado.
    """
    feature_to_ice_lines = Dict({}).tag(sync=True)
    two_way_pds = ListTraitlet([]).tag(sync=True)

    two_way_pdp_extent = ListTraitlet([0, 0]).tag(sync=True)
    two_way_interaction_extent = ListTraitlet([0, 0]).tag(sync=True)

    one_way_pdp_extent = ListTraitlet([0, 0]).tag(sync=True)
    ice_line_extent = ListTraitlet([0, 0]).tag(sync=True)
    ice_cluster_center_extent = ListTraitlet([0, 0]).tag(sync=True)
    centered_ice_line_extent = ListTraitlet([0, 0]).tag(sync=True)

    height = Int(600).tag(sync=True)

    highlighted_indices = ListTraitlet([]).tag(sync=True)

    two_way_to_calculate = ListTraitlet([]).tag(sync=True)

    cluster_update = Dict({}).tag(sync=True)

    def __init__(
        self,
        predict: Callable[[pd.DataFrame], List[float]],
        df: pd.DataFrame,
        labels: Union[List[float], List[int], np.ndarray, pd.Series],
        pd_data: Union[str, Path, dict],
        seed: Union[int, None] = None,
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

            # In JSON, object keys are all strings. Here, we convert
            # ints back to ints.
            for info in pd_data["feature_info"].values():
                if "value_map" in info:
                    info["value_map"] = convert_keys_to_ints(info["value_map"])

        # synced widget state

        self.feature_names = sorted([p["x_feature"] for p in pd_data["one_way_pds"]])
        self.feature_info = pd_data["feature_info"]

        self.dataset = pd_data["dataset"]

        self.num_instances = pd_data["num_instances"]

        self.one_way_pds = pd_data["one_way_pds"]
        self.feature_to_ice_lines = pd_data["feature_to_ice_lines"]
        self.two_way_pds = pd_data["two_way_pds"]

        self.two_way_pdp_extent = pd_data["two_way_pdp_extent"]
        self.two_way_interaction_extent = pd_data["two_way_interaction_extent"]

        self.one_way_pdp_extent = pd_data["one_way_pdp_extent"]
        self.ice_line_extent = pd_data["ice_line_extent"]
        self.ice_cluster_center_extent = pd_data["ice_cluster_center_extent"]
        self.centered_ice_line_extent = pd_data["centered_ice_line_extent"]

        self.height = height

        self.labels = (
            labels.tolist() if isinstance(labels, (np.ndarray, pd.Series)) else labels
        )

        # not synced
        self.df = df
        self.predict = predict
        # TODO: should this be recalculated after any changes to one_way_pds?
        self.feature_to_pd = _get_feature_to_pd(self.one_way_pds)
        self.one_hot_encoded_col_name_to_feature = pd_data[
            "one_hot_encoded_col_name_to_feature"
        ]

        seed_sequence = SeedSequence(seed)
        self.random_state = RandomState(MT19937(seed_sequence))

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

        result = _calc_two_way_pd(
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

    @observe("cluster_update")
    def _on_cluster_update_change(self, change):
        update = change["new"]

        if not update:
            return

        feature = update["feature"]
        prev_num_clusters = update["prev_num_clusters"]
        source_cluster_id = update["source_cluster_id"]
        dest_cluster_id = update["dest_cluster_id"]
        indices_list = update["indices"]
        indices_set = set(indices_list)

        # get the data for this feature

        pd_index, owp = next(
            (i, p) for i, p in enumerate(self.one_way_pds) if p["x_feature"] == feature
        )

        owp = copy.deepcopy(owp)
        ice = owp["ice"]

        ice_lines = np.array(self.feature_to_ice_lines[feature])
        centered_ice_lines = ice_lines - ice_lines[:, 0].reshape(-1, 1)
        centered_pdp = np.array(ice["centered_pdp"])

        clustering = ice["adjusted_clusterings"].get(
            str(prev_num_clusters), ice["clusterings"][str(prev_num_clusters)]
        )

        clusters_indices = {
            cluster["id"]: cluster["indices"] for cluster in clustering["clusters"]
        }

        # move indices from source to dest

        source_cluster_indices_set = set(clusters_indices[source_cluster_id])
        clusters_indices[source_cluster_id] = sorted(
            source_cluster_indices_set.difference(indices_set)
        )
        clusters_indices[dest_cluster_id] = sorted(
            clusters_indices.get(dest_cluster_id, []) + indices_list
        )

        # handle if the source cluster is now empty
        if not clusters_indices[source_cluster_id]:
            del clusters_indices[source_cluster_id]
            old_cluster_ids = sorted(list(clusters_indices.keys()))
            old_to_new = {
                old_cid: new_cid for (new_cid, old_cid) in enumerate(old_cluster_ids)
            }
            clusters_indices = {
                old_to_new[cid]: indices for (cid, indices) in clusters_indices.items()
            }

        new_num_clusters = len(clusters_indices.keys())

        # get new labels

        index_and_label = sorted(
            [
                (idx, cluster_id)
                for cluster_id, indices in clusters_indices.items()
                for idx in indices
            ]
        )
        labels = np.array([label for (_, label) in index_and_label])

        # update cluster distances and means

        ice["adjusted_clusterings"][str(new_num_clusters)] = _get_clusters_info(
            labels,
            new_num_clusters,
            centered_ice_lines,
            centered_pdp,
            self.df,
            self.one_hot_encoded_col_name_to_feature,
            self.random_state,
        )

        ice["num_clusters"] = new_num_clusters

        # update the extents

        one_ways = self.one_way_pds.copy()
        one_ways[pd_index] = owp

        ice_cluster_center_min = math.inf
        ice_cluster_center_max = -math.inf

        for owp in one_ways:
            ice = owp["ice"]
            str_n_clust = str(ice["num_clusters"])

            if str_n_clust in ice["clusterings"]:
                clustering = ice["clusterings"][str_n_clust]
                if clustering["centered_mean_min"] < ice_cluster_center_min:
                    ice_cluster_center_min = clustering["centered_mean_min"]

                if clustering["centered_mean_max"] > ice_cluster_center_max:
                    ice_cluster_center_max = clustering["centered_mean_max"]

        self.ice_cluster_center_extent = [
            ice_cluster_center_min,
            ice_cluster_center_max,
        ]

        self.one_way_pds = one_ways
