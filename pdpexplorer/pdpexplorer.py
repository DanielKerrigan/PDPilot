#!/usr/bin/env python
# coding: utf-8

"""
TODO: Add module docstring
"""

from pathlib import Path
import json
from ipywidgets import DOMWidget
from traitlets import Unicode, List, Int, Dict

from pdpexplorer.metadata import Metadata
from ._frontend import module_name, module_version


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

    height = Int(600).tag(sync=True)

    def __init__(
        self,
        predict,
        df,
        pd_data,
        one_hot_features=None,
        categorical_features=None,
        ordinal_features=None,
        n_jobs=1,
        height=600,
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

        # model predict function
        self.predict = predict

        # pandas dataframe
        self.df = df
        self.md = Metadata(df, one_hot_features, categorical_features, ordinal_features)

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

        self.height = height
        self.n_jobs = n_jobs
