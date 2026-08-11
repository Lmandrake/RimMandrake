import numpy as np, json
g=np.load('ship_grid.npy'); ship=(g!=''); tiles=np.argwhere(ship)
cx=32
# lateral extent
xs=tiles[:,1]
print("x range:",xs.min(),"..",xs.max(),"  max |x-cx|:",max(abs(xs.min()-cx),abs(xs.max()-cx)))
# widest wing row: how far laterally must an on-axis (x=cx) extender reach?
# For a tile at (y,x), nearest on-keel extender at (ey,cx): dist^2=(y-ey)^2+(x-cx)^2 <=16^2
# worst case lateral alone: |x-cx| must be <=16 for SOME extender at same y. check per tile handled already.
place=json.load(open('placements.json'))
# chain rule verification: order matters. Re-simulate strictly.
def disk(cy,ccx,r):
    ys,xx=tiles[:,0],tiles[:,1]; return (ys-cy)**2+(xx-ccx)**2<=r*r
covered=disk(place[0][1],place[0][2],place[0][3])
ok=True
for typ,cy,ccx,r in place[1:]:
    idx=np.where((tiles[:,0]==cy)&(tiles[:,1]==ccx))[0]
    inside = len(idx)>0 and covered[idx[0]]
    if not inside: ok=False; print("CHAIN VIOLATION at",cy,ccx)
    covered=covered|disk(cy,ccx,r)
print("chain rule satisfied:",ok)
print("final covered:",covered.sum(),"/",len(tiles))
# Per-wing worst lateral tile distance to its nearest chosen extender
exts=[(p[1],p[2]) for p in place]
maxd=0
for (y,x) in tiles:
    d=min(((y-ey)**2+(x-ex)**2)**.5 for ey,ex in exts)
    maxd=max(maxd,d)
print("max distance any tile to nearest node: %.2f (must be <=16 for ext / 19 eng)"%maxd)
