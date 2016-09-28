# cripple 20
python -u -m src.combine_rfam_bitscore --query=rfam75id-rename --cripple=20 --nn=7 --inc-centroids 
python -u -m src.normalize_bitscore --tag=rfam75id-rename.cripple20 --query=rfam75id-rename --lengthnorm 
python -u -m src.clustering --tag=rfam75id-rename.cripple20 --alg=labelSpreading --kernel=rbf --alpha=0.8 --gamma=0.4 --multilabel
python -u -m src.cluster_refinement --tag=rfam75id-rename.cripple20 --alg=labelSpreading --c=1.0 --merge
python -u -m src.evaluate --file=results/combined.rfam75id-rename.cripple20.labelSpreading.refined.cluster --query=rfam75id-rename 
# cripple 15
python -u -m src.combine_rfam_bitscore --query=rfam75id-rename --cripple=15 --nn=7 --inc-centroids 
python -u -m src.normalize_bitscore --tag=rfam75id-rename.cripple15 --query=rfam75id-rename --lengthnorm 
python -u -m src.clustering --tag=rfam75id-rename.cripple15 --alg=labelSpreading --kernel=rbf --alpha=0.8 --gamma=0.4 --multilabel
python -u -m src.cluster_refinement --tag=rfam75id-rename.cripple15 --alg=labelSpreading --c=1.0 --merge
python -u -m src.evaluate --file=results/combined.rfam75id-rename.cripple15.labelSpreading.refined.cluster --query=rfam75id-rename 
# cripple 10
python -u -m src.combine_rfam_bitscore --query=rfam75id-rename --cripple=10 --nn=7 --inc-centroids 
python -u -m src.normalize_bitscore --tag=rfam75id-rename.cripple10 --query=rfam75id-rename --lengthnorm 
python -u -m src.clustering --tag=rfam75id-rename.cripple10 --alg=labelSpreading --kernel=rbf --alpha=0.8 --gamma=0.4 --multilabel
python -u -m src.cluster_refinement --tag=rfam75id-rename.cripple10 --alg=labelSpreading --c=1.0 --merge
python -u -m src.evaluate --file=results/combined.rfam75id-rename.cripple10.labelSpreading.refined.cluster --query=rfam75id-rename 
# cripple 5
python -u -m src.combine_rfam_bitscore --query=rfam75id-rename --cripple=5 --nn=7 --inc-centroids 
python -u -m src.normalize_bitscore --tag=rfam75id-rename.cripple5 --query=rfam75id-rename --lengthnorm 
python -u -m src.clustering --tag=rfam75id-rename.cripple5 --alg=labelSpreading --kernel=rbf --alpha=0.8 --gamma=0.4 --multilabel
python -u -m src.cluster_refinement --tag=rfam75id-rename.cripple5 --alg=labelSpreading --c=1.0 --merge
python -u -m src.evaluate --file=results/combined.rfam75id-rename.cripple5.labelSpreading.refined.cluster --query=rfam75id-rename 
# cripple 2
python -u -m src.combine_rfam_bitscore --query=rfam75id-rename --cripple=2 --nn=7 --inc-centroids 
python -u -m src.normalize_bitscore --tag=rfam75id-rename.cripple2 --query=rfam75id-rename --lengthnorm 
python -u -m src.clustering --tag=rfam75id-rename.cripple2 --alg=labelSpreading --kernel=rbf --alpha=0.8 --gamma=0.4 --multilabel
python -u -m src.cluster_refinement --tag=rfam75id-rename.cripple2 --alg=labelSpreading --c=1.0 --merge
python -u -m src.evaluate --file=results/combined.rfam75id-rename.cripple2.labelSpreading.refined.cluster --query=rfam75id-rename 
# cripple 0
python -u -m src.combine_rfam_bitscore --query=rfam75id-rename --cripple=0 --nn=7 --inc-centroids 
python -u -m src.normalize_bitscore --tag=rfam75id-rename.cripple0 --query=rfam75id-rename --lengthnorm 
python -u -m src.clustering --tag=rfam75id-rename.cripple0 --alg=labelSpreading --kernel=rbf --alpha=0.8 --gamma=0.4 --multilabel
python -u -m src.cluster_refinement --tag=rfam75id-rename.cripple0 --alg=labelSpreading --c=1.0 --merge
python -u -m src.evaluate --file=results/combined.rfam75id-rename.cripple0.labelSpreading.refined.cluster --query=rfam75id-rename 
