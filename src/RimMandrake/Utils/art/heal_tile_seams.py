"""Make a nearly-tiling RGBA steam tile truly tile by spreading each seam's difference over a ramp (no ghosting)."""
import sys
from PIL import Image
import numpy as np
BAND=120
def heal(p,axis):
    # p H,W,4 float premultiplied; axis 1: left/right
    p=np.moveaxis(p,axis,0)  # now seam across first index
    d=p[-1]-p[0]             # right - left
    n=p.shape[0]
    r=(1-np.arange(BAND)/BAND)**2
    sh=(BAND,)+(1,)*(p.ndim-1)
    r=r.reshape(sh)
    q=p.copy()
    q[:BAND]+=r*d*0.5
    q[-BAND:]-=r[::-1]*d*0.5
    return np.moveaxis(q,0,axis)
for src,dst in zip(sys.argv[1::2],sys.argv[2::2]):
    a=np.asarray(Image.open(src).convert('RGBA')).astype(np.float64)/255
    pm=np.dstack([a[...,:3]*a[...,3:],a[...,3]])
    for _ in range(3):
        pm=heal(pm,1); pm=heal(pm,0)
    pm=np.clip(pm,0,1)
    al=pm[...,3]
    fill=np.array([0.90,0.93,0.95])  # steam white where alpha is nil, so bilinear never fringes dark
    rgb=np.where(al[...,None]>0.02,pm[...,:3]/np.maximum(al[...,None],1e-3),fill)
    rgb=np.clip(rgb,0,1)
    out=np.dstack([rgb,al])
    Image.fromarray((out*255+.5).astype('uint8'),'RGBA').save(dst,optimize=True)
    o=(out*255)
    print(dst,'seam LR',np.abs(o[:,0]-o[:,-1]).mean().round(2),'TB',np.abs(o[0]-o[-1]).mean().round(2),'alpha mean',o[...,3].mean().round(1))
