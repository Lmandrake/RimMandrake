import numpy as np, json

W, H = 64, 92
g = np.zeros((H, W), dtype='<U1')
def fill(x0,y0,x1,y1,code): g[y0:y1, x0:x1] = code
cx = W//2  # 32

# BOW command core
fill(cx-7, 5, cx+7, 13, 'M')            # 14x8 = 112

# KEEL spine width 5, rows 13..79
fill(cx-2, 13, cx+3, 80, 'K')           # 5 wide

# Corridor stubs from keel to each wing (count as circulation, code '.')
def wing(side_left, y0, code, w=10, h=11):
    if side_left:
        x1 = cx-3; x0 = x1-w
        # connector
        g[y0+h//2, x0+w:cx-2] = '.'
    else:
        x0 = cx+4; x1 = x0+w
        g[y0+h//2, cx+3:x0] = '.'
    fill(x0, y0, x1, y0+h, code)

# Pair 1
wing(False, 15, 'E', w=10, h=11)   # adv materials (hot) right
wing(True , 15, 'F', w=10, h=11)   # precision left
# Pair 2
wing(False, 28, 'B', w=11, h=11)   # bulk/dirty (hot) right slightly bigger
wing(True , 28, 'D', w=10, h=11)   # textile/ammo left
# Pair 3
wing(False, 41, 'A', w=10, h=11)   # raw extraction right
wing(True , 41, 'C', w=10, h=11)   # food left

# Carbonite bay (small luxury) left, pair 3.5
fill(cx-13, 54, cx-3, 60, 'T')     # 10x6=60

# HABITAT ring: belly band rows 62..76
fill(cx-15, 62, cx+16, 76, 'R')
fill(cx-2, 62, cx+3, 80, 'K')      # keel back through

# STERN thrusters/fuel/power
fill(cx-11, 80, cx+12, 88, 'S')

codes = {'M':'Command core','K':'Keel/utility spine','.':'Corridors (circulation)',
 'F':'Wing F precision','E':'Wing E adv-materials (hot)','D':'Wing D textile/ammo',
 'B':'Wing B bulk/dirty (hot)','C':'Wing C food','A':'Wing A raw extraction',
 'R':'Habitat ring','T':'Carbonite bay','S':'Stern thrusters/fuel/power'}
tot=0; counts={}
for c,name in codes.items():
    n=int((g==c).sum()); tot+=n; counts[c]=n
    print(f"{c} {name:34s} {n:5d}")
print("-"*47); print(f"TOTAL connected tiles: {tot}   (cap 2000, headroom {2000-tot})")
factory=sum(counts[c] for c in 'FEDBCA')
print(f"  factory wings total: {factory}  (doc ~652)")
print(f"  living/habitat: {counts['R']}  systems(M+K+S): {counts['M']+counts['K']+counts['S']}  carbonite: {counts['T']}  circ: {counts['.']}")
ys,xs=np.where(g!=''); print("bbox tiles:",xs.max()-xs.min()+1,"x",ys.max()-ys.min()+1)
np.save('ship_grid.npy', g)
