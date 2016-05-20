# NoFold-SSL
A variation of the original NoFold by using semi-supervised approach in the clustering phase. This approach was tested to run (very) much faster comparing to the original NoFold algorithm with a comparable clustering quality. Our three test scenarios showed 1 win 1 draw and 1 lose, the differences are very marginal.

## Concepts
Early concepts are from the NoFold RNA clustering itself which uses some help from Rfam's covariance models for each RNA family to transform an RNA sequence into a vector in high-dimension euclidean space. (1 CM per dimension–total 1,973)

Having all RNA sequences translated to a vector in an euclidean space, we can now cluster the sequences using traditional clustering algorithms, not restricting ourselves from using only distance-based clustering algorithms.

In this project, we aim to introduce a semi-supervised clustering approach to the RNA clustering problem. In so doing, we take "seeds" from each Rfam family as initial settings for the semi-supervised clustering. After that, we use label propagation to label those without "family" labels. It is expected that this process will generate a less-than-actual number of clusters especially when we don't have seeds for every possible family.

The final process is to tailor the clustering results by splitting and merging many times until covergence. We will split the cluster if the merge-distance of points in the cluster is "more" than the "local" inter-cluster distance. One may think this as a realization of the clustering concept which states inter-cluster distance shall be greater than the intra- one. Consequently, if the convergence is not met, we will merge the clusters together where the centroids of the clusters have the same family of nearest "seed" centroid.

## Requirements
If you also want to use NoFold (for comparison), you definitely need to meet the NoFold software requirements which are:

* Python 2.X
* Infernal (v.1.0.2) (*NOT the newest version, which doesn't contain cmscore)
* R with fastcluster package 
* LocARNA 

But, for NoFold-SSL itself you will need:

* Python 2.X with numpy, scipy, scikit-learn and fastcluster packages
* Infernal (v.1.0.2)

## Getting Started
In this repo, we included three datasets, namely "query", "query2", "query3", which can be used right away.

The following commands will guide you how to run this algorithm and arrive with the final clustering results.

```
python combine_rfam_bitscore.py --query=query --cripple=8 --sample=5 --high_density=false && \
python pca_normalize_bitscore.py --tag=query.cripple8 && \
python cluster_semi_label_propagation.py --tag=query.cripple8 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query.cripple8 --alg=labelPropagation --C=1.1
```

The files involved are:

* `combine_rfam_bitscore.py` – combine 'seed' and 'query' in to the same file. The options we are using here `--query` is the name of task and dataset `--cripple` is the number of 'seed' families that appear in the query but shall not be included in the 'seed' `--sample` is the number of samples taken for each seed family (might not be met) `--high_density` if this is true all the samples will not be taken randomly but high density first.
* `pca_normalize_bitscore.py` – run PCA on the combined bitscore file, after that run the Z-normalization.
* `cluster_semi_label_propagation.py` – first step clustering using label propagation options are `--kernel` can be either "knn" or "rbf" `--nn` is the number of nearest neighbors for knn kernel `--gamma` is the gamma for rbf kernel.
* `cluster_refinement_further_seprataion.py` – last step clustering this further refines the clusters by separating, by local inter-cluster distance , and merging many times. `--C` is a parameter that multiplies the local inter-cluster distance, if this number is high the separating phase will not work really hard (number of clusters is lower).
