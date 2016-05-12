import sys
from os.path import isfile, join, isdir, exists
from os import listdir, stat
from Bio import SeqIO
import numpy as np
from sklearn.neighbors import KernelDensity
from sklearn.grid_search import GridSearchCV
import matplotlib.pyplot as plt

path = 'Rfam-seed/db'

families = [f for f in listdir(path) if isdir(join(path, f))]

def get_db_size(family):
    file = join(path, family, family + '.db')
    st = stat(file)
    return st.st_size

file_sizes = np.array(list(map(get_db_size, families)))
x_grid = np.linspace(0, len(file_sizes), len(file_sizes))

# get the mean
print('avg:', file_sizes.mean())

# visualize the sizes
fig, ax = plt.subplots()
ax.plot(x_grid, file_sizes, alpha=0.5)
# ax.legend(loc='upper left')
ax.set_xlim(0, 2000)
plt.show()