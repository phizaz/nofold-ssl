# NoFold-SSL
A variation of the original NoFold by using semi-supervised approach in the clustering phase

## Requirements
If you also want to use NoFold (for comparison), you definitely need to meet the NoFold software requirements which are:

* Python 2.X
* Infernal (v.1.0.2) (*NOT the newest version, which doesn't contain cmscore)
* R with fastcluster package 
* LocARNA 

But, for NoFold-SSL itself you will need:

* Python 2.X with numpy, scipy, scikit-learn and fastcluster packages
* Infernal (v.1.0.2)

### Getting Started
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
* `pca_normalize_bitscore.py` – run PCA on the combined bitscore file, after that run the Z-normalization
* `cluster_semi_label_propagation.py` – first step clustering using label propagation options are `--kernel` can be either "knn" or "rbf" `--nn` is the number of nearest neighbors for knn kernel `--gamma` is the gamma for rbf kernel.
* `cluster_refinement_further_seprataion.py` – last step clustering this further refines the clusters by separating, by local inter-cluster distance , and merging many times. `--C` is a parameter that multiplies the local inter-cluster distance, if this number is high the separating phase will not work really hard (number of clusters is lower).