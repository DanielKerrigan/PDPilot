#!/usr/bin/env python
# coding: utf-8

"""
TODO: Add module docstring
"""

from itertools import combinations
from operator import itemgetter
from pathlib import Path
import json
from ipywidgets import DOMWidget
from traitlets import Unicode, List, Bool, Int, Dict, observe

from pdpexplorer.metadata import Metadata
from ._frontend import module_name, module_version
from .pdp import get_marginal_distributions, widget_partial_dependence
from .logging import log
from scipy.stats import iqr as inner_quartile_range


class PDPExplorerWidget(DOMWidget):
    """TODO: Add docstring here"""

    _model_name = Unicode("PDPExplorerModel").tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode("PDPExplorerView").tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    """widget state that is synced between backend and frontend"""

    features = List([]).tag(sync=True)

    selected_features = List([]).tag(sync=True)
    resolution = Int(20).tag(sync=True)
    num_instances_used = Int(100).tag(sync=True)
    total_num_instances = Int(100).tag(sync=True)

    single_pdps = List([]).tag(sync=True)
    double_pdps = List([]).tag(sync=True)

    one_way_quantitative_clusters = List([]).tag(sync=True)
    one_way_categorical_clusters = List([]).tag(sync=True)

    plot_button_clicked = Int(0).tag(sync=True)

    prediction_extent = List([0, 0]).tag(sync=True)

    marginal_distributions = Dict({}).tag(sync=True)

    def __init__(
        self,
        predict,
        df,
        pd_data,
        feature_to_one_hot=None,
        n_jobs=1,
        quant_threshold=12,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # if pd_data is a path or string, then read the file at that path
        if isinstance(pd_data, Path) or isinstance(pd_data, str):
            path = Path(pd_data).resolve()

            if not path.exists():
                raise OSError(f"Cannot read {path}")

            json_data = path.read_text()
            pd_data = json.loads(json_data)

        # model predict function
        self.predict = predict

        # pandas dataframe
        self.df = df
        self.md = Metadata(df, feature_to_one_hot, quant_threshold=quant_threshold)

        self.features = sorted([p["x_feature"] for p in pd_data["one_way_pds"]])

        self.total_num_instances = self.md.size
        self.num_instances_used = pd_data["n_instances"]
        self.resolution = pd_data["resolution"]

        self.marginal_distributions = pd_data["marginal_distributions"]

        self.single_pdps = pd_data["one_way_pds"]
        self.double_pdps = pd_data["two_way_pds"]
        self.prediction_extent = pd_data["prediction_extent"]

        self.one_way_quantitative_clusters = pd_data["one_way_quantitative_clusters"]
        self.one_way_categorical_clusters = pd_data["one_way_categorical_clusters"]

        self.n_jobs = n_jobs

    @observe("plot_button_clicked")
    def on_plot_button_clicked(self, _):
        """calculate the PDPs when the plot button is clicked"""
        subset = self.df.sample(n=self.num_instances_used)

        self.marginal_distributions = get_marginal_distributions(
            df=subset, features=self.features, md=self.md
        )

        iqr = inner_quartile_range(self.predict(subset))

        single_pdps = widget_partial_dependence(
            predict=self.predict,
            subset=subset,
            features=self.selected_features,
            resolution=self.resolution,
            md=self.md,
            n_jobs=self.n_jobs,
            iqr=iqr,
        )

        min_pred_single = min(single_pdps, key=itemgetter("min_prediction"))[
            "min_prediction"
        ]
        max_pred_single = max(single_pdps, key=itemgetter("max_prediction"))[
            "max_prediction"
        ]

        self.single_pdps = single_pdps
        self.prediction_extent = [min_pred_single, max_pred_single]

        pairs = combinations(self.selected_features, 2)

        double_pdps = widget_partial_dependence(
            predict=self.predict,
            subset=subset,
            features=pairs,
            resolution=self.resolution,
            md=self.md,
            n_jobs=self.n_jobs,
            one_way_pds=self.single_pdps,
        )

        min_pred_double = min(double_pdps, key=itemgetter("min_prediction"))[
            "min_prediction"
        ]
        max_pred_double = max(double_pdps, key=itemgetter("max_prediction"))[
            "max_prediction"
        ]

        self.prediction_extent = [
            min(min_pred_single, min_pred_double),
            max(max_pred_single, max_pred_double),
        ]

        self.double_pdps = double_pdps
