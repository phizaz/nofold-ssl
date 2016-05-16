# query
python combine_rfam_bitscore.py --query=query --cripple=8 --sample=5 --high_density=false && \
python pca_normalize_bitscore.py --tag=query.cripple8 && \
python cluster_semi_label_propagation.py --tag=query.cripple8 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query.cripple8 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query.cripple8 --linkage=ward && \

python combine_rfam_bitscore.py --query=query --cripple=25 --sample=5 --high_density=false && \
python pca_normalize_bitscore.py --tag=query.cripple25 && \
python cluster_semi_label_propagation.py --tag=query.cripple25 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query.cripple25 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query.cripple25 --linkage=ward

# query 2
python combine_rfam_bitscore.py --query=query2 --cripple=4 --sample=5 --high_density=false && \
python pca_normalize_bitscore.py --tag=query2.cripple4 && \
python cluster_semi_label_propagation.py --tag=query2.cripple4 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query2.cripple4 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query2.cripple4 --linkage=ward && \

python combine_rfam_bitscore.py --query=query2 --cripple=10 --sample=5 --high_density=false && \
python pca_normalize_bitscore.py --tag=query2.cripple10 && \
python cluster_semi_label_propagation.py --tag=query2.cripple10 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query2.cripple10 --alg=labelPropagation --C=1.1
python cluster_unsupervised_lmethod.py --tag=query2.cripple10 --linkage=ward

# query 3
python combine_rfam_bitscore.py --query=query3 --cripple=3 --sample=5 --high_density=false && \
python pca_normalize_bitscore.py --tag=query3.cripple3 && \
python cluster_semi_label_propagation.py --tag=query3.cripple3 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query3.cripple3 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query3.cripple3 --linkage=ward && \

python combine_rfam_bitscore.py --query=query3 --cripple=9 --sample=5 --high_density=false && \
python pca_normalize_bitscore.py --tag=query3.cripple9 && \
python cluster_semi_label_propagation.py --tag=query3.cripple9 --kernel=knn --nn=7 && \
python cluster_refinement_further_seprataion.py --tag=query3.cripple9 --alg=labelPropagation --C=1.1 && \
python cluster_unsupervised_lmethod.py --tag=query3.cripple9 --linkage=ward