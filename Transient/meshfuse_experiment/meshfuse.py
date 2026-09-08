"""
meshfuse.py -- Prototype: fuse multiple posed 2D facings onto a TripoSR mesh so
the MESH owns geometry (consistent facings) while the 2D views supply surface
texture, blending across views preferring the head-on view at grazing angles.

Headless-CUDA note: pytorch3d / nvdiffrast both need to COMPILE a CUDA extension
(nvcc). The cu128 venv here has only ptxas from the nvidia-cuda-nvcc wheel (no
nvcc/cicc frontend), so neither builds. This uses a pure-numpy software
rasterizer instead (z-buffer + barycentric gouraud), which needs no compiler and
tests the same hypothesis. torch/CUDA present but not required.

Pipeline:
  1. load mesh (vertex-colored, no UVs) -> per-vertex color bake target
  2. ALIGNMENT GATE: render untextured silhouettes, search az x elev per
     reference (S/E/N) to maximize silhouette IoU. Report best pose + IoU.
  3. FUSION BAKE: project each reference onto vertices at its best pose,
     weighting by max(0, normal.viewdir)**k (head-on preference) and z-buffer
     visibility. Unseen vertices keep original TripoSR color.
  4. re-render clean orthographic S/E/N from fused vertex colors.
  5. contact sheet: input | raw-TripoSR | fused, columns S/E/N.
"""
import os, sys, time
import numpy as np
import trimesh
from PIL import Image

HERE = "/mnt/d/Luke/dev/Rimworld/Transient/meshfuse_experiment"
MESH = "/mnt/d/Luke/dev/Rimworld/Transient/triposr_prototype/output/0/mesh.obj"
REFDIR = "/mnt/d/Luke/dev/Rimworld/src/RimMandrake/WreckedMachines/art_source/AutomatedSmelter/repaired"
TRIPOSR_FACINGS = "/mnt/d/Luke/dev/Rimworld/Transient/triposr_prototype/output/0"
os.makedirs(os.path.join(HERE, "renders"), exist_ok=True)
os.makedirs(os.path.join(HERE, "work"), exist_ok=True)

VIEWS = ["south", "east", "north"]          # the 3 fitting views
BASE_AZ = {"south": 0.0, "east": 90.0, "north": 180.0}   # TripoSR convention (prior render_facings)

# ---------------------------------------------------------------- camera
def cam_basis(az_deg, el_deg):
    az, el = np.radians(az_deg), np.radians(el_deg)
    cam_dir = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    forward = -cam_dir
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, up); n = np.linalg.norm(right)
    if n < 1e-6:  # looking straight down: pick a stable right
        right = np.array([1.0, 0.0, 0.0]); forward = np.array([0.0,0.0,-np.sign(el) or -1.0])
    else:
        right = right/n
    true_up = np.cross(right, forward)
    return cam_dir, forward, right, true_up

def project(verts, az, el):
    cam_dir, forward, right, true_up = cam_basis(az, el)
    c = verts.mean(0)
    rel = verts - c
    x = rel @ right
    y = rel @ true_up
    d = rel @ forward          # larger = farther
    return x, y, d, forward

# ---------------------------------------------------------------- rasterizer
def rasterize(x, y, depth, faces, W, H, vcolor=None, vnormal_wt=None,
              fit_bbox=None, supersample=1):
    """Software z-buffer rasterizer. Returns (rgba uint8, coverage mask, faceidx, bary).
    If vcolor given -> gouraud RGB. Fits projected bbox into WxH (aspect-preserving,
    90% fill) unless fit_bbox=(cx,cy,scale) supplied. Painter via per-pixel z-min."""
    Ws, Hs = W*supersample, H*supersample
    # fit projected coords to pixel space
    if fit_bbox is None:
        xmin,xmax,ymin,ymax = x.min(),x.max(),y.min(),y.max()
        cx,cy = (xmin+xmax)/2,(ymin+ymax)/2
        span = max(xmax-xmin, (ymax-ymin))*1.11
        scale = min(Ws,Hs)/span
    else:
        cx,cy,scale = fit_bbox; scale*=supersample
    px = (x-cx)*scale + Ws/2
    py = Hs/2 - (y-cy)*scale       # flip y for image coords
    zb = np.full((Hs,Ws), np.inf, np.float32)
    fb = np.full((Hs,Ws), -1, np.int32)
    # barycentric buffers
    bA = np.zeros((Hs,Ws,3), np.float32)
    fv = faces
    ax,ay = px[fv[:,0]],py[fv[:,0]]
    bx,by = px[fv[:,1]],py[fv[:,1]]
    cxx,cyy = px[fv[:,2]],py[fv[:,2]]
    area = (bx-ax)*(cyy-ay)-(cxx-ax)*(by-ay)
    fd = depth[fv].mean(1)
    # cull: back-of-frame + degenerate + facing away already handled by caller mask
    keep = np.abs(area) > 1e-9
    idx = np.where(keep)[0]
    # sort far->near so nearer overwrites (we still z-test)
    order = idx[np.argsort(-fd[idx])]
    for f in order:
        x0,x1,x2 = ax[f],bx[f],cxx[f]; y0,y1,y2 = ay[f],by[f],cyy[f]
        minx=int(max(0,np.floor(min(x0,x1,x2)))); maxx=int(min(Ws-1,np.ceil(max(x0,x1,x2))))
        miny=int(max(0,np.floor(min(y0,y1,y2)))); maxy=int(min(Hs-1,np.ceil(max(y0,y1,y2))))
        if maxx<minx or maxy<miny: continue
        xx,yy = np.meshgrid(np.arange(minx,maxx+1), np.arange(miny,maxy+1))
        xx=xx.astype(np.float32)+0.5; yy=yy.astype(np.float32)+0.5
        ar = area[f]
        w0 = ((x1-xx)*(y2-yy)-(x2-xx)*(y1-yy))/ar
        w1 = ((x2-xx)*(y0-yy)-(x0-xx)*(y2-yy))/ar
        w2 = 1.0-w0-w1
        inside = (w0>=-1e-4)&(w1>=-1e-4)&(w2>=-1e-4)
        if not inside.any(): continue
        z = w0*depth[fv[f,0]]+w1*depth[fv[f,1]]+w2*depth[fv[f,2]]
        yi = yy.astype(int)[inside]-0; xi = xx.astype(int)[inside]
        yi = (yy[inside]-0.5).astype(int); xi=(xx[inside]-0.5).astype(int)
        zi = z[inside]
        cur = zb[yi,xi]
        better = zi < cur
        if not better.any(): continue
        yi,xi,zi = yi[better],xi[better],zi[better]
        zb[yi,xi]=zi; fb[yi,xi]=f
        bA[yi,xi,0]=w0[inside][better]; bA[yi,xi,1]=w1[inside][better]; bA[yi,xi,2]=w2[inside][better]
    cov = fb>=0
    out = np.zeros((Hs,Ws,4), np.float32)
    if vcolor is not None:
        ff = fb[cov]
        w = bA[cov]
        col = (w[:,0:1]*vcolor[fv[ff,0]] + w[:,1:2]*vcolor[fv[ff,1]] + w[:,2:3]*vcolor[fv[ff,2]])
        out[cov,:3]=col; out[cov,3]=1.0
    else:
        out[cov,3]=1.0; out[cov,:3]=0.6
    # downsample supersample
    if supersample>1:
        out = out.reshape(H,supersample,W,supersample,4).mean((1,3))
        cov = out[...,3]>0.5
    rgba=(np.clip(out,0,1)*255).astype(np.uint8)
    return rgba, cov, fb, bA, (cx if fit_bbox is None else fit_bbox[0])

# ---------------------------------------------------------------- silhouette IoU
def alpha_bbox(mask):
    ys,xs=np.where(mask)
    if len(xs)==0: return None
    return xs.min(),xs.max(),ys.min(),ys.max()

def fit_mask_to_ref(mesh_mask, ref_mask):
    """UNIFORM-scale mesh silhouette so its bbox max-dim matches ref bbox max-dim,
    center on ref bbox, IoU over ref crop. Preserves aspect -> penalizes a tall
    mesh silhouette matched against a wide reference (diagnostic here)."""
    mb=alpha_bbox(mesh_mask); rb=alpha_bbox(ref_mask)
    if mb is None or rb is None: return 0.0
    mcrop=mesh_mask[mb[2]:mb[3]+1, mb[0]:mb[1]+1]
    mh,mw=mcrop.shape
    rw,rh=rb[1]-rb[0]+1, rb[3]-rb[2]+1
    s=min(rw/mw, rh/mh)                      # uniform scale to fit inside ref bbox
    nw,nh=max(1,int(round(mw*s))), max(1,int(round(mh*s)))
    m_img=np.asarray(Image.fromarray((mcrop*255).astype(np.uint8)).resize((nw,nh),Image.NEAREST))>127
    canvas=np.zeros((rh,rw),bool)
    oy,ox=(rh-nh)//2,(rw-nw)//2
    canvas[oy:oy+nh,ox:ox+nw]=m_img
    rcrop=ref_mask[rb[2]:rb[3]+1, rb[0]:rb[1]+1]
    inter=(canvas&rcrop).sum(); uni=(canvas|rcrop).sum()
    return inter/uni if uni else 0.0

def quick_silhouette(verts, faces, fnormals, az, el, W, H):
    """Fast low-res silhouette: splat all vertices to a mask + dilate to fill.
    Vertex density (91k) >> low-res pixels so silhouette is accurate; occlusion
    irrelevant for a silhouette (union of all projected surface)."""
    x,y,d,forward = project(verts,az,el)
    xmin,xmax,ymin,ymax=x.min(),x.max(),y.min(),y.max()
    cx,cy=(xmin+xmax)/2,(ymin+ymax)/2; span=max(xmax-xmin,ymax-ymin)*1.11
    scale=min(W,H)/span
    px=((x-cx)*scale+W/2).astype(int); py=(H/2-(y-cy)*scale).astype(int)
    m=(px>=0)&(px<W)&(py>=0)&(py<H)
    mask=np.zeros((H,W),bool); mask[py[m],px[m]]=True
    # dilate 3x3 twice to close vertex-spacing gaps
    for _ in range(2):
        d2=mask.copy()
        d2[1:,:]|=mask[:-1,:]; d2[:-1,:]|=mask[1:,:]
        d2[:,1:]|=mask[:,:-1]; d2[:,:-1]|=mask[:,1:]
        mask=d2
    return mask

# ---------------------------------------------------------------- main
def main():
    t0=time.time()
    m=trimesh.load(MESH,force="mesh",process=False)
    V=np.asarray(m.vertices,np.float64); F=np.asarray(m.faces,np.int64)
    VC=np.asarray(m.visual.vertex_colors)[:,:3].astype(np.float32)/255.0
    m.fix_normals()  # consistent winding for normals
    VN=np.asarray(m.vertex_normals,np.float64)
    FN=np.asarray(m.face_normals,np.float64)
    print(f"mesh {len(V)} v {len(F)} f  loaded {time.time()-t0:.1f}s")

    refs={}
    for v in VIEWS+["west"]:
        im=np.asarray(Image.open(os.path.join(REFDIR,f"AutomatedSmelter_{v}.png")).convert("RGBA"))
        refs[v]=im
    # ---- ALIGNMENT GATE: search az,el per reference for best silhouette IoU
    SW=160
    gate={}
    az_grid=list(range(0,360,15))
    el_grid=[0,15,22,35,50,70,88]
    for v in VIEWS:
        ref=refs[v]; rmask=ref[...,3]>20
        H,W=ref.shape[:2]
        # low-res ref mask
        rlo=np.asarray(Image.fromarray((rmask*255).astype(np.uint8)).resize((SW,int(SW*H/W)),Image.NEAREST))>127
        best=(-1,None,None)
        for az in az_grid:
            for el in el_grid:
                sm=quick_silhouette(V,F,FN,az,el,SW,int(SW*H/W))
                iou=fit_mask_to_ref(sm,rlo)
                if iou>best[0]: best=(iou,az,el)
        gate[v]=best
        base=BASE_AZ[v]
        # also eval the prior-convention pose for reference
        smb=quick_silhouette(V,F,FN,base,22,SW,int(SW*H/W))
        iou_base=fit_mask_to_ref(smb,rlo)
        print(f"GATE {v:6s}: best IoU {best[0]:.3f} @ az={best[1]} el={best[2]}  |  prior(az={base},el22) IoU {iou_base:.3f}")
    # choose poses: use best-fit pose per view for baking
    poses={v:(gate[v][1],gate[v][2]) for v in VIEWS}

    # ---- FUSION BAKE onto vertex colors
    bake_col=VC.copy()
    acc=np.zeros((len(V),3),np.float64); accw=np.zeros(len(V),np.float64)
    K=3.0  # head-on preference exponent
    for v in VIEWS:
        az,el=poses[v]; ref=refs[v]; H,W=ref.shape[:2]
        x,y,d,forward=project(V,az,el)
        viewdir=-forward
        ndv=VN@viewdir
        front=ndv>0.05
        # z-buffer visibility: render depth of front faces, test each vertex
        ff=(FN@viewdir)>0
        _,cov,fb,bA,_=rasterize(x,y,d,F[ff],W,H)
        # need pixel coords consistent with rasterize's fit -> recompute same fit
        xmin,xmax,ymin,ymax=x.min(),x.max(),y.min(),y.max()
        cx,cy=(xmin+xmax)/2,(ymin+ymax)/2; span=max(xmax-xmin,ymax-ymin)*1.11
        scale=min(W,H)/span
        px=(x-cx)*scale+W/2; py=H/2-(y-cy)*scale
        # depth buffer from cov: build zbuf via same raster returning depth
        zbuf=np.full((H,W),np.inf,np.float32)
        # recompute a proper zbuffer quickly using face raster depths
        # (reuse fb: for each covered pixel we know face -> its mean depth is coarse;
        #  instead approximate vertex visibility by comparing vertex depth to nearest covered)
        # Simpler robust test: vertex visible if its projected pixel is covered AND
        # its depth within tol of the min depth among front faces at that pixel.
        # Build zbuf by splatting front-face vertex depths (min).
        ix=np.round(px).astype(int); iy=np.round(py).astype(int)
        vmask=(ix>=0)&(ix<W)&(iy>=0)&(iy<H)&front
        # min-depth splat
        order=np.argsort(-d)  # far first so near overwrites
        zt=np.full((H,W),np.inf,np.float32)
        oi=order[vmask[order]]
        zt[iy[oi],ix[oi]]=np.minimum(zt[iy[oi],ix[oi]], d[oi]) if False else d[oi]
        # proper min:
        zt=np.full((H,W),np.inf,np.float32)
        for k in order:
            if not vmask[k]: continue
            if d[k]<zt[iy[k],ix[k]]: zt[iy[k],ix[k]]=d[k]
        tol=(d.max()-d.min())*0.03+1e-6
        vis=np.zeros(len(V),bool)
        vv=np.where(vmask)[0]
        vis[vv]=(d[vv]<=zt[iy[vv],ix[vv]]+tol)&cov[iy[vv],ix[vv]]
        # sample reference color at vertex pixel
        rgb=ref[...,:3].astype(np.float32)/255.0; a=ref[...,3].astype(np.float32)/255.0
        sv=np.where(vis)[0]
        col=rgb[iy[sv],ix[sv]]; al=a[iy[sv],ix[sv]]
        w=np.maximum(0,ndv[sv])**K * al
        acc[sv]+=col*w[:,None]; accw[sv]+=w
        print(f"BAKE {v:6s} az={az} el={el}: {vis.sum()} verts textured  ({100*vis.mean():.0f}%)")
    seen=accw>1e-6
    bake_col[seen]=(acc[seen]/accw[seen,None]).astype(np.float32)
    print(f"total verts textured by fusion: {seen.sum()} ({100*seen.mean():.0f}%)")

    # ---- RE-RENDER clean orthographic S/E/N from fused colors (flat, no shade)
    def render_facing(colors,az,el,W,H,ss=2):
        x,y,d,forward=project(V,az,el)
        ff=(FN@(-forward))>0
        rgba,_,_,_,_=rasterize(x,y,d,F[ff],W,H,vcolor=colors,supersample=ss)
        return rgba
    fused_imgs={}; raw_imgs={}
    for v in VIEWS:
        az,el=poses[v]; H,W=refs[v].shape[:2]
        fused_imgs[v]=render_facing(bake_col,az,el,W,H)
        raw_imgs[v]=render_facing(VC,az,el,W,H)
        Image.fromarray(fused_imgs[v]).save(os.path.join(HERE,"renders",f"fused_{v}.png"))
        Image.fromarray(raw_imgs[v]).save(os.path.join(HERE,"renders",f"rawmesh_{v}.png"))

    # ---- CONTACT SHEET: 3 rows (input / raw TripoSR mesh / fused) x 3 cols (S/E/N)
    CELL=300; PAD=12; LBL=120
    rows=["INPUT sprite","RAW TripoSR mesh","FUSED mesh"]
    def fit(img,cell):
        im=Image.fromarray(img).convert("RGBA")
        im.thumbnail((cell,cell),Image.LANCZOS)
        bg=Image.new("RGBA",(cell,cell),(30,30,34,255))
        bg.alpha_composite(im,((cell-im.width)//2,(cell-im.height)//2))
        return bg
    from PIL import ImageDraw
    Wc=LBL+3*(CELL+PAD)+PAD; Hc=PAD+40+3*(CELL+PAD)
    sheet=Image.new("RGBA",(Wc,Hc),(20,20,24,255)); dr=ImageDraw.Draw(sheet)
    for j,v in enumerate(VIEWS):
        dr.text((LBL+PAD+j*(CELL+PAD)+CELL//2-20,10),v.upper(),fill=(230,230,230,255))
    for i,(label,imgset) in enumerate(zip(rows,[refs,raw_imgs,fused_imgs])):
        y=40+PAD+i*(CELL+PAD)
        dr.text((8,y+CELL//2-6),label,fill=(210,210,210,255))
        for j,v in enumerate(VIEWS):
            cell=fit(imgset[v] if not isinstance(imgset[v],np.ndarray) else imgset[v],CELL)
            sheet.alpha_composite(cell,(LBL+PAD+j*(CELL+PAD),y))
    outp=os.path.join(HERE,"contact_sheet.png")
    sheet.convert("RGB").save(outp)
    print("CONTACT SHEET:",outp)
    # save fused mesh
    m2=trimesh.Trimesh(vertices=V,faces=F,vertex_colors=(np.clip(bake_col,0,1)*255).astype(np.uint8),process=False)
    m2.export(os.path.join(HERE,"fused_mesh.ply"))
    print(f"done {time.time()-t0:.1f}s")

if __name__=="__main__":
    main()
