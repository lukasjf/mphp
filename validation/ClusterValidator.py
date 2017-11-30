from sklearn import metrics

from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

class ClusterValidator():
    def __init__(self):
        self.cluster_table = {
            "kmeans": KMeans,
            "AgglomerativeClustering": AgglomerativeClustering
            #"mixture models"
            #"subspace clustering"
        }

        self.metric_table = {
        "adjusted_rand_index": metrics.adjusted_rand_score,
        "adjusted_mutual_information": metrics.adjusted_mutual_info_score,
        "v_measure": metrics.v_measure_score,
        "fowlkes_mallows": metrics.fowlkes_mallows_score
        }

    def evaluate(self, data, algorithms, measures):
        result = []
        for a in algorithms:
            if a not in self.cluster_table:
                continue
            clustering = self.cluster_table[a]()
            clustering.fit(data.expressions)
            result +=  [self.evaluateClustering(data.labels, clustering.labels_, measures)]
        return result

    def evaluateClustering(self, labels, cluster_labels, measures):
        result = []
        for m in measures:
            if m not in self.metric_table:
                continue
            result += [self.metric_table[m](labels, cluster_labels)]
        return result