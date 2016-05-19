sudo apt-get update

# ssh key, for pushing back to the github repo
ssh-keygen -t rsa -b 4096 -C "email@here.com"

# git
sudo apt-get instal git

# python and pip 
sudo apt-get install python-pip
sudo apt-get install python-numpy python-scipy
pip install numpy scipy biopython scikit-learn fastcluster

# R
sudo apt-get install r-base-core
R
install.packages('fastcluster')

# infernal 
wget http://eddylab.org/software/infernal/infernal-1.0.2.tar.gz
cd infernal-1.0.2
./configure
make -j8
sudo chown -R user /usr/local
make install 

# locarna
sudo apt-add-repository ppa:j-4/vienna-rna && \
sudo apt-add-repository ppa:swill/locarna && \
sudo apt-get update && \
sudo apt-get install locarna

# clone
git clone git@github.com:phizaz/nofold-ssl.git