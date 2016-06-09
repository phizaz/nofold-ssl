from os.path import join
from Bio import SeqIO
from collections import Counter
import gzip
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import SingleLetterAlphabet, RNAAlphabet, DNAAlphabet
from Bio.SeqRecord import SeqRecord

'''
Rename the duplicate sequences
'''

query = 'fam40_typedistributed_bg'
path = join('../queries', query, query + '.db')

selected_fams = ['RF01848', 'RF02044', 'RF00727', 'RF02402', 'RF01607', 'RF01687', 'RF01685', 'RF02375', 'RF02514', 'RF01660', 'RF01225', 'RF01323', 'RF01689', 'RF00052', 'RF01786', 'RF02089', 'RF01482', 'RF01909', 'RF01929', 'RF01833', 'RF01501', 'RF01500', 'RF01505', 'RF01504', 'RF01506', 'RF01293', 'RF00381', 'RF00027', 'RF02045', 'RF00222', 'RF00104', 'RF00103', 'RF01930', 'RF01931', 'RF01932', 'RF01933', 'RF01934', 'RF01496', 'RF01499', 'RF01498']

def fam_of(name):
    return to_fam[name]

names_taken = Counter()
def decorate_name(fam, name):
    new_name = fam + '_' + name.split('/')[0]
    names_taken[new_name] += 1
    if names_taken[new_name] > 1:
        new_name += ':' + str(names_taken[new_name])
    return new_name

def get_unique_name(record):
    if record.name.split('_')[0] == 'bg':
        return ('bg', record.name, str(record.seq))
    else:
        return (fam_of(record.name), decorate_name(fam_of(record.name), record.name), str(record.seq))

def bioseq_of((fam, name, sequence)):
    return SeqRecord(Seq(sequence, SingleLetterAlphabet),
                     id=name, name=name, description='')

def save_records(file, records):
    seq_records = map(bioseq_of, records)
    with open(file, 'w') as handle:
        SeqIO.write(seq_records, handle, 'fasta')

rfam_path = '/Volumes/Konpat/Rfam 12.1'
to_fam = dict()
for fam in selected_fams:
    print('fam:', fam)
    with gzip.open(join(rfam_path, fam + '.fa.gz')) as handle:
        raw_records = map(lambda x: (fam, x.name, str(x.seq)), SeqIO.parse(handle, 'fasta'))
        for fam, name, seq in raw_records:
            to_fam[name] = fam

with open(path, 'r') as handle:
    records = map(get_unique_name, SeqIO.parse(handle, 'fasta'))
    # for record in records:
    #     print(record)

save_records(path, records)