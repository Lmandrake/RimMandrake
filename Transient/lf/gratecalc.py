import pickle
d = pickle.load(open(r'/mnt/d/Luke/dev/Rimworld/Transient/lf/west.pkl','rb'))
sub, top, walls = d['sub'], d['top'], d['walls']
X0, X1, Z0, Z1 = 80, 102, 126, 165   # broken ankle + leg
def has_sub(c): return bool(sub.get(c))
# connected components of no-foundation, non-wall cells (8-conn); touching box edge = outside
voids = {(x,z) for x in range(X0,X1+1) for z in range(Z0,Z1+1)
         if not has_sub((x,z)) and (x,z) not in walls}
seen, holes = set(), []
for start in sorted(voids):
    if start in seen: continue
    comp, stack, edge = [], [start], False
    seen.add(start)
    while stack:
        c = stack.pop(); comp.append(c)
        x, z = c
        if x in (X0, X1) or z in (Z0, Z1): edge = True
        for dx in (-1,0,1):
            for dz in (-1,0,1):
                n = (x+dx, z+dz)
                if n in voids and n not in seen:
                    seen.add(n); stack.append(n)
    if not edge: holes.append(comp)
cand = set()
for comp in holes:
    for (x,z) in comp:
        for dx in (-1,0,1):
            for dz in (-1,0,1):
                n = (x+dx, z+dz)
                if n == (x,z) or n in walls: continue
                if has_sub(n) and 'XGrate' not in str(top.get(n)):
                    cand.add(n)
print('interior holes:', [(len(c), sorted(c)[:4]) for c in holes])
print('cells to grate:', len(cand))
for c in sorted(cand): print(c, top.get(c))
ops = ';'.join(f'guy762_FloorTiles_XGrate_iron:{x},{z},1,1' for (x,z) in sorted(cand))
open(r'/mnt/d/Luke/dev/Rimworld/Transient/lf/grate_ops.txt','w').write(ops)
