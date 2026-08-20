import numpy as np
g = np.load('ship_grid.npy')
GH,GW = g.shape
ship = (g!='')
tiles = np.argwhere(ship)   # (y,x)
N = len(tiles)
print("ship tiles:", N)

R_ENG=19.0; R_EXT=16.0
# Engine + extenders placed on the keel (x≈cx). cx=32 in this grid.
# Keel runs y=13..88. Put engine mid-spine, extenders chained up & down.
cx=32
# candidate spine y positions
def disk(cy,cx,r):
    ys,xs = tiles[:,0],tiles[:,1]
    return (ys-cy)**2 + (xs-cx)**2 <= r*r

# Greedy: engine central, then extenders to cover remaining, each extender
# must sit within currently-connected field (chain rule).
eng=(50,cx)  # mid
covered = disk(*eng,R_ENG)
placements=[('ENGINE',eng,R_ENG)]
# candidate extender centers: along keel every few tiles
cand=[(y,cx) for y in range(14,89,1)]
# also allow slight x offset into wide bands
for _ in range(6):
    best=None;best_gain=-1;best_c=None
    for (cy,ccx) in cand:
        # extender must be on connected substructure => within current covered set
        # find if this tile is currently covered
        idx=np.where((tiles[:,0]==cy)&(tiles[:,1]==ccx))[0]
        if len(idx)==0: continue
        if not covered[idx[0]]: continue   # chain rule: must be inside field
        newcov = covered | disk(cy,ccx,R_EXT)
        gain = newcov.sum()-covered.sum()
        if gain>best_gain:
            best_gain=gain;best=(cy,ccx);best_c=newcov
    if best is None: break
    covered=best_c
    placements.append(('EXT',best,R_EXT))

print("placed:",len(placements)-1,"extenders")
print("covered:",covered.sum(),"/",N,"  uncovered:",N-covered.sum())
for p in placements: print("  ",p)
# capacity
cap=500+250*(len(placements)-1)
print("capacity:",cap,"  tiles:",N,"  capacity_ok:",N<=cap)
np.save('coverage.npy',covered)
import json
json.dump([[t[0],int(t[1][0]),int(t[1][1]),t[2]] for t in placements],open('placements.json','w'))
