
Usage
=====

The UI is organized into three tabs: One-way Plots, Two-way Plots, and Detailed Plot.

One-way Plots
-------------

The One-way Plots tab shows a grid of PDP + ICE plots, each containing one feature. Each plot shows the ICE lines in gray and the partial dependence line in black.  Above the plots, there is a row of controls. The arrow buttons allow you to change pages. The “ICE” dropdown menu controls the type of visualization shown. The default is the standard ICE plot. Alternatively, you can show centered ICE plots, where all of the lines start at y = 0. Lastly, you can cluster the ICE lines and show the mean of each cluster. The “Scale locally” checkbox determines whether each plot has the same y-axis or each plot has its y-axis scaled to fit its own data. For normal ICE plots, scaling locally may not have any effect if the ICE lines already take up the full range of y-values. The "Distributions" checkbox toggles whether or not the marginal distributions of the features are shown above the plots. Brushing the lines on an ICE plot highlights the lines for those instances across all of the plots.

The “Sort” dropdown menu controls how the plots are sorted. The one-way plots can be ranked according to one of several metrics:

* **Variance**: Ranks the plots in descending order of the average amount of variance in the y-values (prediction target) of their ICE lines. The plots that have more variation are ranked higher.
* **Cluster difference**: Ranks the plots in descending order of the total distance from the centers of the ICE line clusters to the partial dependence line. The plots that have more different clusters are ranked higher. This metric is paired best with the centered or clusters visualizations.
* **Highlighted similarity**: Used in coordination with brushing ICE lines. This metric can be useful to identify if a cluster of instances in one plot is also a cluster in any others. Plots where the highlighted lines are closer together and farther from the partial dependence line are ranked first. The distances are computed on the centered ICE lines, so this metric is best paired with the centered ICE lines visualization. If you change the highlighted instances after selecting this metric, then clicking the refresh button next to the drop-down menu will update the rankings.
* **Highlighted distribution**: Used in coordination with brushing ICE lines. For each plot, this metric measures the distance between the distribution of feature values for the highlighted instances to the distribution for all instances. The plots are sorted in descending order so that the features whose highlighted distributions are most different from the overall distributions are ranked higher. If you change the highlighted instances after selecting this metric, then clicking the refresh button next to the drop-down menu will update the rankings.

On the left sidebar, you can filter the plots by the type of the feature, by the shape of the PDP, and by feature name. Ordered features have values with defined orders, such as quantities. Nominal features have values without defined orders, such as categories. For ordered features, you can filter by whether the feature's PDP is generally increasing, decreasing, or sometimes increasing and sometimes decreasing.

Two-way Plots
-------------

The Two-way Plots tab shows a grid of PDPs, each containing two features. The default color scale visualizes the interactions between the pairs of features. A positive value indicates a positive interaction effect. This means that the features are interacting in a way that make the average prediction higher than expected if there was no interaction. A negative value indicates a negative interaction effect that lowers the model's average prediction compared to what would be expected with no interaction. Using the one-way PDPs for a given pair of features, we can calculate what the two-way PDP would look like if there was no interaction between the two features. We then visualize the difference between the the actual PDP and the calculated PDP with no interaction. Using the "Color" drop-down menu, you can change the color scale to "predictions" in order to show traditional two-way PDPs, where color encodes the model's average prediction.

The two-way plots can be ranked according to the following metrics:

* **Interaction**: This metric ranks the plots in descending order of `Friedman's H-statistic <https://christophm.github.io/interpretable-ml-book/interaction.html>`_.
* **Variance**: This metric ranks the plots in descending order of the amount of variance in the average predictions.

Detailed Plot
-------------

Hovering over any plot in the One-way Plots or Two-way Plots tab will reveal an expand button in the bottom-left corner of the plot. Clicking on this button will show this plot in the Detailed Plot tab. Alternatively, you can directly go to the Detailed Plot tab and choose which feature or pair of features you want to look at in more detail.

For a one-way plot, this tab shows a larger version of the plot and allows you to analyze the clusters in more depth. In this tab, the “Clusters” visualization shows each cluster in its own plot. The ICE lines in each cluster are shown in lighter-colored lines. The mean of each cluster is shown in a darker-colored line. The partial dependence line is shown in black in each plot. In order to understand what kind of instances make up each cluster, you can select the "Describe clusters" checkbox. This visualizes the distributions of the instances in each cluster for a handful of features. PDPilot automatically chooses features that are helpful in separating the clusters.

For a two-way plot, the Detailed Plot tab shows the one-way ICE plots for both features, the two-way PDP, and the two-way interaction PDP. Two-way PDPs are expensive to compute, so for efficiency, PDPilot only computes the two-way PDPs that it expects to show interaction. If you change the features in the Detailed Plot tab, the two-way PDP for the pair that you select may not have been pre-computed. In this case, you can click the “Compute Now” button to calculate the two-way PDP.
