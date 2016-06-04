# query
python combine_rfam_bitscore.py --query=query --cripple=8 --sample=5 && \
python pca_normalize_bitscore.py --tag=query.cripple8 && \
python cluster_semi_label_propagation.py --tag=query.cripple8 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query.cripple8 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query.cripple8 --linkage=ward && \

python combine_rfam_bitscore.py --query=query --cripple=25 --sample=5 && \
python pca_normalize_bitscore.py --tag=query.cripple25 && \
python cluster_semi_label_propagation.py --tag=query.cripple25 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query.cripple25 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query.cripple25 --linkage=ward

# query 2
python combine_rfam_bitscore.py --query=query2 --cripple=4 --sample=5 && \
python pca_normalize_bitscore.py --tag=query2.cripple4 && \
python cluster_semi_label_propagation.py --tag=query2.cripple4 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query2.cripple4 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query2.cripple4 --linkage=ward && \

python combine_rfam_bitscore.py --query=query2 --cripple=10 --sample=5 && \
python pca_normalize_bitscore.py --tag=query2.cripple10 && \
python cluster_semi_label_propagation.py --tag=query2.cripple10 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query2.cripple10 --alg=labelPropagation --C=1.1
python cluster_unsupervised_lmethod.py --tag=query2.cripple10 --linkage=ward

# query 3
python combine_rfam_bitscore.py --query=query3 --cripple=3 --sample=5 && \
python pca_normalize_bitscore.py --tag=query3.cripple3 && \
python cluster_semi_label_propagation.py --tag=query3.cripple3 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query3.cripple3 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query3.cripple3 --linkage=ward && \

python combine_rfam_bitscore.py --query=query3 --cripple=9 --sample=5 && \
python pca_normalize_bitscore.py --tag=query3.cripple9 && \
python cluster_semi_label_propagation.py --tag=query3.cripple9 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query3.cripple9 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query3.cripple9 --linkage=ward

# 1-2-3 synthetic
python combine_rfam_bitscore.py --query=novel-1-2-3hp --unformatted=true --sample=5 && \
python pca_normalize_bitscore.py --tag=novel-1-2-3hp && \
python cluster_semi_label_propagation.py --tag=novel-1-2-3hp --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=novel-1-2-3hp --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=novel-1-2-3hp --linkage=ward

# rfam75id-rename
python combine_rfam_bitscore.py --query=rfam75id-rename --cripple=0 --sample=5 && \
python pca_normalize_bitscore.py --tag=rfam75id-rename.cripple0 && \
python cluster_semi_label_propagation.py --tag=rfam75id-rename.cripple0 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=rfam75id-rename.cripple0 --alg=labelPropagation --C=1.1 --true-centroid=true && \
python cluster_unsupervised_lmethod.py --tag=rfam75id-rename.cripple0 --linkage=ward

# rfam75id-rename (closest)
python combine_rfam_bitscore.py --query=rfam75id-rename --cripple=0 --type=closest --nn=7 && \
python pca_normalize_bitscore.py --tag=rfam75id-rename.cripple0 && \
python cluster_semi_label_propagation.py --tag=rfam75id-rename.cripple0 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=rfam75id-rename.cripple0 --alg=labelPropagation --C=1.1 --true-centroid=false && \
python evaluate.py --file=Rfam-seed/combined.rfam75id-rename.cripple0.labelPropagation.refined.cluster --nofold=false && \
python cluster_unsupervised_lmethod.py --tag=rfam75id-rename.cripple0 --linkage=ward

python evaluate.py --file=Rfam-seed/rfam75id/rfam75id.clusters_s3rSpec_top.txt_expanded_merged_bs17.41bgNoneGloc.txt --nofold=true

