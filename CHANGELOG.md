# Changelog

## 0.6.1

- Added brushing for scatter plots in the Detailed Plots tab for two-way plots.
- Added throttling for the plot brushing to control how often the plots need to be redrawn. This is set through the `brush_throttle_duration` parameter in the `PDPilotWidget` class.
- Added the `opacity` parameter for the `PDPilotWidget` class. This allows the user to set the opacity of the lines in the ICE plots. If the opacity is 1, we can draw paths of the same color in a single stroke, rather than one stroke for each path.
- Added the ability to highlight all of the instances in a given cluster.
- Removed unused code.
- Set random seeds in the examples.
- Updated dependencies.
- Renamed `createSyncedWidget` function to `createSyncedStore`.
- Added changelog.

## 0.6.0

- Fixed bug that would occasionally cause the features in the cluster descriptions to appear in the wrong order.
- Fixed bug that would cause the second to last feature in the dataset to always appear in the cluster descriptions.
- Save the decision tree parameters to fix a bug caused by 0.5.7 that broke editing clusters.
- Changed the `partial_dependence` function to have a single `decision_tree_params` parameter rather than than individual parameters for `max_depth` and `ccp_alpha`. This has the benefit in that now user can set any `DecisionTreeClassifier` parameter, rather than just those two.

## 0.5.7

- Added parameters to `partial_dependence` function for the `max_depth` and `ccp_alpha` parameters for sklearn's `DecisionTreeClassifier` rather than hard coding them.

## 0.5.6

- Changed the default value for `mixed_shape_tolerance` in the `partial_dependence` function from 0.15 to 0.29.
- Updated default detection of nominal and ordinal features.

## 0.5.5

- Added the `cluster_preprocessing` parameter to the `partial_dependence` function to enable the user to change how ICE lines a preprocessed before clustering.
- Added the `compute_two_way_pdps` parameter to the `partial_dependence` function to control whether or not two-way PDPs should be computed.

## 0.5.4

- Fixed bug where a user's specified feature types were sometimes overridden by the defaults if they set `nominal_features` but not `ordinal_features` in the `partial_dependence` function.

## 0.5.3

- Improved logging.
- Added check when computing the plots to skip features that only have a single unique value.
- Updated user study documentation.

## 0.5.2

- This is the version of PDPilot that was used for the user study.
