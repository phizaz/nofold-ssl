class HierarchicalClustMaxMergeDist:
    """
    Agglomerative Clustering with given max merge distance, instead of the number of clusters
    """

    def __init__(self):
        self.X = None
        self.max_merge_dist = None

    def fit(self, X, max_merge_dist, method='ward', metric='euclidean'):
        self.X = X
        self.max_merge_dist = max_merge_dist

        from fastcluster import linkage
        merge_hist = linkage(X, method=method, metric=metric, preserve_input=True)

        from .disjoint import DisjointSet
        disjoint = DisjointSet(len(X))

        # _, _, merge_dists, _ = list(zip(*merge_hist))
        # print('merge_dists:', merge_dists)

        for a, b, merge_dist, _ in merge_hist:
            if merge_dist > max_merge_dist:
                break
            a, b = int(a), int(b)
            disjoint.join(a, b)

        belong_to = [disjoint.parent(i) for i in range(len(X))]

        # rename the cluster name to be 0 -> cluster_count - 1
        cluster_map = {}
        cluster_name = 0
        belong_to_renamed = []
        for each in belong_to:
            if not each in cluster_map:
                cluster_map[each] = cluster_name
                cluster_name += 1
            belong_to_renamed.append(cluster_map[each])

        return belong_to_renamed