
state = None
RF = None
buffer = None

def write(rf, buffer, file):
    with open(file, 'w') as file:
        for line in buffer:
            file.write(line + '\n')

for line in open('Rfam.seed'):
    line = line.strip()

    if state is None:
        if line.find('# STOCKHOLM 1.0') >= 0:
            if buffer is not None:
                write(RF, buffer, 'Rfam-seed/stockholm/' + RF)
            buffer = []
            state = 'find rf'

    if state == 'find rf':
        if line.find('#=GF AC   RF') >= 0:
            tokens = line.split(' ')
            RF = tokens[-1]
            print(RF)
            state = None

    buffer.append(line)