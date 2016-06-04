# query
python combine_rfam_bitscore.py --query=query --cripple=8 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=query.cripple8 && \
python cluster_semi_label_propagation.py --tag=query.cripple8 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=query.cripple8 --alg=labelPropagation --C=1.1 && \
python evaluate.py --tag=query.cripple8 --query=query --nofold=false && \

python combine_rfam_bitscore.py --query=query --cripple=25 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=query.cripple25 && \
python cluster_semi_label_propagation.py --tag=query.cripple25 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=query.cripple25 --alg=labelPropagation --C=1.1 && \
python evaluate.py --tag=query.cripple25 --query=query --nofold=false

# query 2
python combine_rfam_bitscore.py --query=query2 --cripple=4 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=query2.cripple4 && \
python cluster_semi_label_propagation.py --tag=query2.cripple4 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=query2.cripple4 --alg=labelPropagation --C=1.1 && \
python evaluate.py --tag=query2.cripple4 --query=query2 --nofold=false && \

python combine_rfam_bitscore.py --query=query2 --cripple=10 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=query2.cripple10 && \
python cluster_semi_label_propagation.py --tag=query2.cripple10 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=query2.cripple10 --alg=labelPropagation --C=1.1 && \ 
python evaluate.py --tag=query2.cripple10 --query=query2 --nofold=false 

# query 3
python combine_rfam_bitscore.py --query=query3 --cripple=3 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=query3.cripple3 && \
python cluster_semi_label_propagation.py --tag=query3.cripple3 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=query3.cripple3 --alg=labelPropagation --C=1.1 && \
python evaluate.py --tag=query3.cripple3 --query=query3 --nofold=false && \

python combine_rfam_bitscore.py --query=query3 --cripple=9 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=query3.cripple9 && \
python cluster_semi_label_propagation.py --tag=query3.cripple9 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=query3.cripple9 --alg=labelPropagation --C=1.1 && \
python evaluate.py --tag=query3.cripple9 --query=query3 --nofold=false 

# 1-2-3 synthetic
# 2 corse - 212.81s - 100% acc
python combine_rfam_bitscore.py --query=novel-1-2-3hp --unformatted=true --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=novel-1-2-3hp && \
python cluster_semi_label_propagation.py --tag=novel-1-2-3hp --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=novel-1-2-3hp --alg=labelPropagation --C=1.1 --true-centroid=false

# rfam75id-rename (closest)
# 2 cores - 509.28s, 565.83s (NN = 3)
python combine_rfam_bitscore.py --query=rfam75id-rename --cripple=0 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=rfam75id-rename.cripple0 && \
python cluster_semi_label_propagation.py --tag=rfam75id-rename.cripple0 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=rfam75id-rename.cripple0 --alg=labelPropagation --C=1.1 --true-centroid=false && \
python evaluate.py --file=Rfam-seed/combined.rfam75id-rename.cripple0.labelPropagation.refined.cluster --db=Rfam-seed/rfam75id-rename/rfam75id-rename.db --nofold=false

python evaluate.py --file=Rfam-seed/rfam75id/rfam75id.clusters_s3rSpec_top.txt_expanded_merged_bs17.41bgNoneGloc.txt --db=Rfam-seed/rfam75id/rfam75id.db --nofold=true

# rfam75id_dinuc3000-rename (closest)
# 2 cores - 2241.38s, 2387.28s (NN = 3)
python combine_rfam_bitscore.py --query=rfam75id_dinuc3000-rename --cripple=1 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=rfam75id_dinuc3000-rename.cripple1 && \
python cluster_semi_label_propagation.py --tag=rfam75id_dinuc3000-rename.cripple1 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=rfam75id_dinuc3000-rename.cripple1 --alg=labelPropagation --C=1.1 --true-centroid=false && \
python evaluate.py --file=Rfam-seed/combined.rfam75id_dinuc3000-rename.cripple1.labelPropagation.refined.cluster --db=Rfam-seed/rfam75id_dinuc3000-rename/rfam75id_dinuc3000-rename.db --nofold=false

python evaluate.py --file=Rfam-seed/rfam75id_dinuc3000/rfam75id_dinuc3000.clusters_s3rSpec_top.txt_expanded_merged_bs19.64bgNoneGloc.txt --db=Rfam-seed/rfam75id_dinuc3000/rfam75id_dinuc3000.db --nofold=true

# rfam75id_embed-rename (closest)
# 2 cores - 532.83s , 589.38s (NN = 3)
python combine_rfam_bitscore.py --query=rfam75id_embed-rename --cripple=0 --type=closest --nn=3 && \
python pca_normalize_bitscore.py --tag=rfam75id_embed-rename.cripple0 && \
python cluster_semi_label_propagation.py --tag=rfam75id_embed-rename.cripple0 --kernel=rbf --gamma=0.5 && \
python cluster_refinement_further_seprataion.py --tag=rfam75id_embed-rename.cripple0 --alg=labelPropagation --C=1.1 --true-centroid=false && \
python evaluate.py --file=Rfam-seed/combined.rfam75id_embed-rename.cripple0.labelPropagation.refined.cluster --db=Rfam-seed/rfam75id_embed-rename/rfam75id_embed-rename.db --nofold=false 

python evaluate.py --file=Rfam-seed/rfam75id_embed/rfam75id_embed.clusters_s3rSpec_top.txt_expanded_merged_bs17.83bgNoneGloc.txt --db=Rfam-seed/rfam75id_embed/rfam75id_embed.db --nofold=true

