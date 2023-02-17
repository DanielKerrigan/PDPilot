
Usage
=====

The UI is organized into three tabs: One-way Plots, Two-way Plots, and Detailed Plot.

One-way Plots
-------------

The One-way Plots tab shows a grid of PDP + ICE plots, each containing one feature. Each plot shows the ICE lines in light gray and the partial dependence line in black. On the left sidebar, you can filter the plots by the type of the feature, by the shape of the PDP, and by feature name. Above the plots, there is a row of controls. The arrow buttons allow you to change pages. The "Scale locally" checkbox determines whether each plot has the same y-axis or each plot has its y-axis scaled to fit its data. Checking the "Cluster lines" checkbox will cluster the ICE lines in each plot by their shape and show the center of each cluster. The lines in these plots are centered so that they start at y = 0. The "Distributions" checkbox toggles whether or not the marginal distributions of the features are shown above the plots. Brushing the lines on an ICE plot highlights the lines for those instances across all of the plots.

The one-way plots can be ranked according to one of several metrics, chosen via the "Sort by" drop-down list:

* **variance**: This metric ranks the plots in descending order of the average amount of variance in the y-values (prediction target) of their ICE lines.
* **cluster difference**: This metric ranks the plots in descending order of the total distance from the centers of the ICE line clusters to the partial dependence line.
* **complexity**: This metric fits a spline to each PDP, increasing the number of knots in the spline until a good fit is reached. The primary ranking for the plots is in descending order of the number of knots in the spline. The secondary ranking is in descending order of the distance between the spline and the PDP. Note that this metric only applies to quantitative and ordinal features. Nominal features are put at the end.
* **highlighted similarity**: This metric is used in coordination with brushing ICE lines. It ranks the plots in descending order of how close the highlighted lines are together. If you change the highlighted instances after selecting this metric, then clicking the refresh button next to the drop-down menu will update the rankings.
* **highglighted distribution**: This metric is used in coordination with brushing ICE lines. For each plot, it measures the distance between the feature's distribution for the highlighted instances to the distribution for all instances. The plots are sorted in descending order. If you change the highlighted instances after selecting this metric, then clicking the refresh button next to the drop-down menu will update the rankings.

Two-way Plots
-------------

The Two-way Plots tab shows a grid of PDPs, each containing two features. The default color scale visualizes the interactions between the pairs of features. A positive value indicates that the features are interacting in a way that make the average prediction higher than expected if there was no interaction. A negative value indicates that the features are interacting in a way that makes the average prediction lower than expected. Using the one-way PDPs for a given pair of features, we can calculate what the two-way PDP would look like if there was no interaction between the two features. We then visualize the difference between this calculated PDP with no interaction and the true PDP. Using the "Color" drop-down menu, you can change the color scale to "predictions" in order to show traditional two-way PDPs.

The two-way plots can be ranked according to the following metrics:

* **interaction**: This metric ranks the plots in descending order of Friedman's H-statistic.
* **variance**: This metric ranks the plots in descending order of the amount of variance in the average predictions.

Detailed Plot
-------------

Hovering over any plot in the One-way Plots or Two-way Plots tab will reveal an expand button in the bottom-left corner of the plot. Clicking on this button will show this plot in the Detailed Plot tab. Alternatively, you can go to the Detailed Plot tab and choose which feature or pair of features you want to look at in more detail.

For two-way plots, you can see the one-way ICE plots for both features, the two-way PDP, and the two-way PDP showing the interactions.

For one-way plots, the "ICE" drop-down lets you select different ways to visualize the ICE plot.

* **Lines** is the default. It shows the partial dependence line in black and the ICE lines in gray.
* **Cluster Lines** clusters the ICE lines and shows each cluster in its own plot. The mean of each cluster is shown in a darker-colored line. The ICE lines in each cluster are shown in lighter-colored lines. The partial depedence line is shown in black in each plot.
* **Cluster Bands** clusters the ICE lines and shows each cluster in its own plot. The partial depedence line is shown in black in each plot. The mean of each cluster is shown in a darker-colored line. Each plot has a bands that show the 25-75 percentile and 10-90 percentile values of the ICE lines.
* **Cluser Centers** clusters the ICE lines and visualizes the centers of the clusters as gray lines. The partial depedence line is shown in black.

When the Cluster Lines or Cluster Bands visualization is chosen, you can select the "Describe clusters" checkbox to visualize the distributions of the instances in each cluster for a handful of features. The tool chooses features that are helpful in separating the clusters. You can brush the axes in these feature distribution visualziations to filter the ICE lines.
