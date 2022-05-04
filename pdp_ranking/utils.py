import statistics
from itertools import product
from sklearn.inspection import partial_dependence


def generate_pdp(features, model, dataset):
    # Retrieve the partial dependence of the given feature
    result = partial_dependence(model, dataset, [tuple(features)], kind='average')

    if len(features) == 1:
        y = list(result['average'][0])
        x = list(result['values'][0])
        return [{'x': x, 'y': y, 'value': 0} for (x, y) in zip(x, y)]
    elif len(features) == 2:
        grid = product(*result['values'])
        averages = result['average'][0].flatten()
        return [
            {'x': x, 'y': y, 'value': value}
            for (x, y), value in zip(grid, averages)
        ]


def generate_single_pdp(feature_index, feature_name, model, data):
    pdp = partial_dependence(model, data, [feature_index], kind="average")
    ranking_metric = calculate_single_pdp_ranking_metric(pdp)
    return {
        "feature_index": feature_index,
        "feature_name": feature_name,
        "ranking_metric": ranking_metric,
        "pdp_graph_data": generate_pdp([feature_index], model, data),
    }


def generate_double_pdp(feature_tuple, model, data):
    pdp = partial_dependence(model, data, [feature_tuple], kind="average")
    ranking_metric = calculate_double_pdp_ranking_metric(pdp)
    return {
        "features": sorted(list(feature_tuple)),
        "ranking_metric": ranking_metric,
        "pdp_graph_data": generate_pdp(list(feature_tuple), model, data)
    }


def calculate_single_pdp_ranking_metric(pdp):
    """
    Calculates the standard deviation of the y value points to
    determine how "interesting" a single PDP is.
    """
    y = list(pdp['average'][0])
    return statistics.stdev(y)


def calculate_double_pdp_ranking_metric(pdp):
    """
    Calculates the standard deviation of the averages
    """
    averages = pdp['average'][0].flatten()
    return statistics.stdev(averages)