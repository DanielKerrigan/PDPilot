from operator import itemgetter
from itertools import chain
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from plotnine import (
    ggplot,
    geom_line,
    geom_point,
    geom_tile,
    aes,
    labs,
    scale_fill_distiller,
    scale_y_continuous,
    theme_light,
    ggtitle,
    coord_cartesian,
)

from pdpexplorer.ticks import nice, ticks

def plot(
    *,
    data,
    one_way_sort_by=None,
    two_way_sort_by=None,
    same_prediction_scale=True,
    output_path=None,
):
    # if data is a path or string, then read the file at that path
    if isinstance(data, Path) or isinstance(data, str):
        path = Path(data).resolve()

        if not path.exists():
            raise OSError(f"Cannot read {path}")

        json_data = path.read_text(encoding="utf-8")
        data = json.loads(json_data)

    # check that the output path existsm fail early if it doesn't
    if output_path:
        output_path = Path(output_path).resolve()

        if not output_path.exists():
            raise OSError(f"Cannot write to {output_path}")

        one_way_output_path = output_path.joinpath("one_way")
        one_way_output_path.mkdir()

        if data["two_way_pds"]:
            two_way_output_path = output_path.joinpath("two_way")
            two_way_output_path.mkdir()

    min_pred, max_pred = data["pdp_extent"]

    nice_prediction_limits = nice(min_pred, max_pred, 5)
    nice_prediction_breaks = ticks(
        nice_prediction_limits[0], nice_prediction_limits[1], 5
    )

    # one-way

    one_way_pdps = []

    if one_way_sort_by == "good_fit":
        sorted_one_way_pds = sorted(
            data["one_way_pds"],
            key=lambda x: (-x["knots_good_fit"], -x["nrmse_good_fit"]),
        )
    elif one_way_sort_by == "deviation":
        sorted_one_way_pds = sorted(data["one_way_pds"], key=lambda x: -x["deviation"])
    else:
        sorted_one_way_pds = data["one_way_pds"]

    num_digits = math.floor(math.log10(len(sorted_one_way_pds))) + 1

    for i, par_dep in enumerate(sorted_one_way_pds):
        if par_dep["kind"] == "quantitative":
            df = pd.DataFrame(
                {
                    "x_values": par_dep["x_values"],
                    "mean_predictions": par_dep["mean_predictions"],
                    "trend": par_dep["trend_good_fit"],
                }
            )

            pdp = (
                ggplot(data=df, mapping=aes(x="x_values"))
                + geom_line(aes(y="trend"), color="#7C7C7C")
                + geom_line(aes(y="mean_predictions"), color="#792367")
                + labs(x=par_dep["x_feature"], y="prediction")
                + theme_light()
            )

            if same_prediction_scale:
                pdp += coord_cartesian(ylim=nice_prediction_limits, expand=False)
        else:
            df = pd.DataFrame(
                {
                    "x_values": par_dep["x_values"],
                    "mean_predictions": par_dep["mean_predictions"],
                }
            )

            pdp = (
                ggplot(data=df, mapping=aes(x="factor(x_values)", y="mean_predictions"))
                + geom_point(color="#792367")
                + labs(x=par_dep["x_feature"], y="prediction")
                + theme_light()
            )

            if same_prediction_scale:
                pdp += scale_y_continuous(limits=nice_prediction_limits, expand=(0, 0))

        if output_path:
            pdp.save(
                filename=one_way_output_path.joinpath(
                    f'{i:0>{num_digits}}_{par_dep["id"]}.png'
                ),
                format="png",
                dpi=300,
                verbose=False,
            )
        else:
            one_way_pdps.append(pdp)

    # two-way

    two_way_pdps = []

    if data["two_way_pds"]:
        if two_way_sort_by == "h":
            sorted_two_way_pds = sorted(data["two_way_pds"], key=lambda x: -x["H"])
        elif two_way_sort_by == "deviation":
            sorted_two_way_pds = sorted(
                data["two_way_pds"], key=lambda x: -x["deviation"]
            )
        else:
            sorted_two_way_pds = data["two_way_pds"]

        num_digits = math.floor(math.log10(len(sorted_two_way_pds))) + 1

        for i, par_dep in enumerate(sorted_two_way_pds):
            limits_and_breaks = (
                {"limits": nice_prediction_limits, "breaks": nice_prediction_breaks}
                if same_prediction_scale
                else {}
            )

            if par_dep["kind"] == "quantitative":
                df = pd.DataFrame(
                    {
                        "x_values": par_dep["x_values"],
                        "y_values": par_dep["y_values"],
                        "mean_predictions": par_dep["mean_predictions"],
                    }
                )

                pdp = (
                    ggplot(data=df, mapping=aes(x="x_values", y="y_values"))
                    + geom_tile(mapping=aes(fill="mean_predictions"))
                    + scale_fill_distiller(
                        palette="YlGnBu", direction=1, **limits_and_breaks
                    )
                    + labs(
                        fill="prediction",
                        x=par_dep["x_feature"],
                        y=par_dep["y_feature"],
                    )
                    + ggtitle(f'H* = {par_dep["H"]:.3f}')
                    + theme_light()
                )
            elif par_dep["kind"] == "categorical":
                df = pd.DataFrame(
                    {
                        "x_values": par_dep["x_values"],
                        "y_values": par_dep["y_values"],
                        "mean_predictions": par_dep["mean_predictions"],
                    }
                )

                pdp = (
                    ggplot(
                        data=df, mapping=aes(x="factor(x_values)", y="factor(y_values)")
                    )
                    + geom_tile(mapping=aes(fill="mean_predictions"))
                    + scale_fill_distiller(
                        palette="YlGnBu", direction=1, **limits_and_breaks
                    )
                    + labs(
                        fill="prediction",
                        x=par_dep["x_feature"],
                        y=par_dep["y_feature"],
                    )
                    + ggtitle(f'H* = {par_dep["H"]:.3f}')
                    + theme_light()
                )
            else:
                df = pd.DataFrame(
                    {
                        "x_values": par_dep["x_values"],
                        "y_values": par_dep["y_values"],
                        "mean_predictions": par_dep["mean_predictions"],
                    }
                )

                pdp = (
                    ggplot(data=df, mapping=aes(x="x_values", y="factor(y_values)"))
                    + geom_tile(mapping=aes(fill="mean_predictions"))
                    + scale_fill_distiller(
                        palette="YlGnBu", direction=1, **limits_and_breaks
                    )
                    + labs(
                        fill="prediction",
                        x=par_dep["x_feature"],
                        y=par_dep["y_feature"],
                    )
                    + ggtitle(f'H* = {par_dep["H"]:.3f}')
                    + theme_light()
                )

            if output_path:
                pdp.save(
                    filename=two_way_output_path.joinpath(
                        f'{i:0>{num_digits}}_{par_dep["id"]}.png'
                    ),
                    format="png",
                    dpi=300,
                    verbose=False,
                )
            else:
                two_way_pdps.append(pdp)

    if not output_path:
        return one_way_pdps, two_way_pdps

