import pickle
d = pickle.load(open(r'/mnt/d/Luke/dev/Rimworld/Transient/lf/west.pkl','rb'))
sub, top, walls = d['sub'], d['top'], d['walls']
from collections import Counter
print('top terrain histogram (region):', Counter(str(v) for v in top.values()).most_common(12))
X0, X1, Z0, Z1 = 80, 112, 124, 168
for z in range(Z1, Z0-1, -1):
    row = ''
    for x in range(X0, X1+1):
        t = str(top.get((x,z)))
        if (x,z) in walls: ch='#'
        elif 'XGrate' in t: ch='X'
        elif t == 'Substructure': ch='o'    # bare substructure
        elif sub.get((x,z)): ch='.'         # substructure + real floor
        else: ch=' '
        row += ch
    print(f'{z:3d} {row}')
print('    ' + ''.join(str(x%10) for x in range(X0, X1+1)))
