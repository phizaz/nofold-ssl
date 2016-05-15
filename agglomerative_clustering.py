from fastcluster import linkage

class DisjointSet:
    def __init__(self, sets_cnt):
        self.level_parent = [i for i in range(2 * sets_cnt - 1)]
        self.highest = sets_cnt

    def parent(self, node):
        if node != self.level_parent[node]:
            self.level_parent[node] = self.parent(self.level_parent[node])
        return self.level_parent[node]

    def join(self, a, b):
        parent_a = self.parent(a)
        parent_b = self.parent(b)

        if a == b:
            raise Exception('joining the same set')

        self.level_parent[parent_a] = self.highest
        self.level_parent[parent_b] = self.highest

        # prevent trees to be tall
        self.parent(a)
        self.parent(b)

        self.highest += 1

    def common(self, a, b):
        return self.parent(a) == self.parent(b)

class AgglomerativeClusteringMaxMergeDist:
    """
    Agglomerative Clustering with given max merge distance, instead of the number of clusters
    """

    def __init__(self):
        self.X = None
        self.cluster_centers_ = None
        self.max_merge_dist = None

    def get_centroids(self, X, belong_to):
        clusters_cnt = max(belong_to) + 1
        acc_centroids_by_group = [np.zeros(X[0].shape) for i in range(clusters_cnt)]
        cluster_member_cnt = [0 for i in range(clusters_cnt)]
        for i, x in enumerate(X):
            belongs = belong_to[i]
            cluster_member_cnt[belongs] += 1
            acc_centroids_by_group[belongs] += x

        centroids = [acc_centroid / member_cnt
                     for acc_centroid, member_cnt
                     in zip(acc_centroids_by_group, cluster_member_cnt)]

        return centroids, cluster_member_cnt

    def fit(self, X, max_merge_dist, method='ward', metric='euclidean'):
        self.X = X
        self.max_merge_dist = max_merge_dist

        merge_hist = linkage(X, method=method, metric=metric, preserve_input=True)

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