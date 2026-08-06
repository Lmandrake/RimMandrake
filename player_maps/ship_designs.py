"""
ship_designs.py  —  Gravship topology canvas + coverage verifier.

Two constant sets: VANILLA (verified) and EXPANDED (Bigger Gravships, assumed
pending Fetcher 2026-08-06_bigger_gravships_ranges). The active limits are the
EXPANDED block below; swap to the VAN_* values to re-check against vanilla.

  * ONE grav engine  : connects tiles within radius R_ENG
  * up to N_EXT extenders : each connects tiles within radius R_EXT
  * CHAIN RULE        : an extender only extends the field if it is itself
                        inside the field built by the engine + earlier extenders
  * CAPACITY CAP      : <= CAP connected substructure tiles total
A design is LIFTABLE iff (tiles <= CAP) AND (every ship tile lies inside the
final grav field) AND (extenders used <= N_EXT satisfy the chain rule).
place_and_verify stops adding extenders once the hull is fully covered, so the
reported n_ext_used is how many are actually NEEDED (not always the max).

Each design supplies:
  - a grid of single-char zone codes ('' = empty / not-ship)
  - a BACKBONE mask (tiles where the engine + extenders are allowed to sit;
    physically the keel/spine, must be real ship tiles)
Nodes (engine + 6 extenders) are auto-placed greedily on the backbone to
MAXIMISE covered ship tiles, then the result is verified.
"""
import numpy as np, json

# ---- VANILLA limits (kept for reference) --------------------------------
VAN_R_ENG, VAN_R_EXT, VAN_CAP, VAN_N_EXT = 19, 16, 2000, 6

# ---- EXPANDED limits (Bigger Gravships, APPROVED 2026-08-06) -------------
# Generous ASSUMED values pending the real slider ranges (Fetcher
# 2026-08-06_bigger_gravships_ranges). Chosen to widen the authoring space
# for large/cool Star Wars silhouettes while keeping ships ship-shaped.
# Re-validate against the real numbers when the Fetcher result lands.
R_ENG   = 34     # grav engine connection radius   (vanilla 19)
R_EXT   = 30     # field extender connection radius (vanilla 16)
CAP     = 4800   # total connected substructure cap (vanilla 2000)
N_EXT   = 12     # max field extenders             (vanilla 6)

# ---- zone palette (shared with renderer) --------------------------------
# Palette scheme (per user, 2026-08-06):
#   * SYSTEM / "caps" regions = FULL SATURATION, fixed hues:
#       command=BLUE, habitat=GREEN, water=CYAN, cargo=BROWN,
#       thrusters=YELLOW, carbonite=BLACK, corridor=GREY (+ fuel, keel structural)
#   * FACTORY wings (A,B,C,D,E,F) = PASTELS, spread around the hue wheel.
COL = {
    # --- system / structural regions: full saturation ---
    'M':(30,80,230),    # command / control        -> BLUE
    'R':(35,180,55),    # habitat ring             -> GREEN
    'W':(0,200,235),    # water tanks              -> CYAN
    'G':(135,78,30),    # cargo hold               -> BROWN
    'S':(250,220,15),   # stern thrusters + power  -> YELLOW
    'T':(12,12,16),     # carbonite / trophy       -> BLACK
    '.':(150,150,155),  # corridor / cross-deck    -> GREY
    'U':(190,35,165),   # fuel tanks (system)      -> saturated MAGENTA
    'H':(245,245,248),  # shuttle bay / hangar     -> WHITE
    'K':(70,72,82),     # keel / spine (structural, dark slate)
    # --- factory wings: pastels ---
    'F':(203,172,232),  # precision           -> pastel violet
    'E':(246,166,160),  # advanced materials  -> pastel coral (HOT)
    'B':(250,201,150),  # bulk / dirty        -> pastel orange (HOT)
    'C':(245,233,152),  # food                -> pastel yellow
    'D':(176,226,198),  # textile / ammo      -> pastel mint
    'A':(222,190,196),  # raw extraction      -> pastel dusty-rose
}
LABEL = {
    'M':'Command / control','K':'Keel / utility spine','G':'Cargo hold',
    'F':'Precision factory','E':'Adv. materials (HOT)','B':'Bulk / dirty (HOT)',
    'C':'Food','D':'Textile / ammo','A':'Raw extraction','R':'Habitat','W':'Water tanks',
    'U':'Fuel tanks','S':'Thrusters + power','T':'Carbonite / trophy',
    'H':'Shuttle bay / hangar','.':'Corridor / cross-deck',
}

# ---- grid helpers -------------------------------------------------------
class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = np.full((h, w), '', dtype='<U1')
        self.bb = np.zeros((h, w), dtype=bool)   # backbone mask
    def rect(self, x0, y0, x1, y1, code):
        x0,x1 = sorted((x0,x1)); y0,y1 = sorted((y0,y1))
        self.g[y0:y1+1, x0:x1+1] = code
    def disk(self, cx, cy, r, code, only_empty=False):
        yy,xx = np.mgrid[0:self.h,0:self.w]
        m = (xx-cx)**2+(yy-cy)**2 <= r*r
        if only_empty: m &= (self.g=='')
        self.g[m] = code
    def ring(self, cx, cy, r_out, r_in, code):
        yy,xx = np.mgrid[0:self.h,0:self.w]
        d2 = (xx-cx)**2+(yy-cy)**2
        self.g[(d2<=r_out*r_out)&(d2>=r_in*r_in)] = code
    def carve(self, x0,y0,x1,y1):          # set back to empty (courtyard)
        x0,x1=sorted((x0,x1)); y0,y1=sorted((y0,y1))
        self.g[y0:y1+1,x0:x1+1]=''
    def carve_disk(self, cx, cy, r):
        yy,xx=np.mgrid[0:self.h,0:self.w]
        self.g[(xx-cx)**2+(yy-cy)**2 <= r*r]=''
    def poly(self, pts, code, only_empty=False):
        """Fill a polygon (list of (x,y)) with code. Even-odd rule."""
        ys=[p[1] for p in pts]; xs=[p[0] for p in pts]
        y0,y1=max(0,int(min(ys))),min(self.h-1,int(max(ys)))
        n=len(pts)
        for y in range(y0,y1+1):
            xints=[]
            for i in range(n):
                x_i,y_i=pts[i]; x_j,y_j=pts[(i+1)%n]
                if (y_i<=y<y_j) or (y_j<=y<y_i):
                    t=(y-y_i)/(y_j-y_i)
                    xints.append(x_i+t*(x_j-x_i))
            xints.sort()
            for k in range(0,len(xints)-1,2):
                xa=max(0,int(np.ceil(xints[k]))); xb=min(self.w-1,int(np.floor(xints[k+1])))
                for x in range(xa,xb+1):
                    if only_empty and self.g[y,x]!='': continue
                    self.g[y,x]=code
    def taper(self, cx, y0, y1, hw0, hw1, code):
        """A trapezoid spine: half-width interpolates hw0->hw1 from y0->y1."""
        y0,y1=int(y0),int(y1)
        for y in range(min(y0,y1),max(y0,y1)+1):
            t=(y-y0)/max(1,(y1-y0))
            hw=int(round(hw0+(hw1-hw0)*t))
            self.rect(cx-hw,y,cx+hw,y,code)
    def backbone_rect(self, x0,y0,x1,y1):
        x0,x1=sorted((x0,x1)); y0,y1=sorted((y0,y1))
        self.bb[y0:y1+1,x0:x1+1]=True
    def octagon(self, cx, cy, r, code, only_empty=False):
        """Filled regular octagon of 'radius' r (flat-to-flat ~2r)."""
        yy,xx=np.mgrid[0:self.h,0:self.w]
        dx=np.abs(xx-cx); dy=np.abs(yy-cy)
        cut=int(round(r*1.4142))               # chamfer for the diagonals
        m=(dx<=r)&(dy<=r)&((dx+dy)<=cut)
        if only_empty: m &= (self.g=='')
        self.g[m]=code
    def spoke(self, x0, y0, x1, y1, half, code, backbone=True):
        """A thick straight corridor from (x0,y0) to (x1,y1), 2*half+1 wide,
        wide enough for belt-in + belt-out + walking. Optionally lay backbone
        down its centerline so nodes/extenders can chain along the spoke."""
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        xs=np.linspace(x0,x1,n); ys=np.linspace(y0,y1,n)
        for xf,yf in zip(xs,ys):
            xi,yi=int(round(xf)),int(round(yf))
            self.rect(xi-half,yi-half,xi+half,yi+half,code)
        if backbone:
            for xf,yf in zip(xs,ys):
                xi,yi=int(round(xf)),int(round(yf))
                if 0<=yi<self.h and 0<=xi<self.w: self.bb[yi,xi]=True
    def ship_mask(self):
        return self.g!=''
    def crop(self):
        ys,xs=np.where(self.ship_mask())
        if len(xs)==0: return
        x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
        pad=1
        self.g=self.g[max(0,y0-pad):y1+2, max(0,x0-pad):x1+2]
        self.bb=self.bb[max(0,y0-pad):y1+2, max(0,x0-pad):x1+2]
        self.h,self.w=self.g.shape

# ---- coverage verifier --------------------------------------------------
def _disk_mask(h,w,cx,cy,r):
    yy,xx=np.mgrid[0:h,0:w]
    return (xx-cx)**2+(yy-cy)**2 <= r*r

def place_and_verify(canvas):
    """Greedily place engine + 6 extenders on the backbone to maximise
    coverage of ship tiles, obeying the chain rule. Returns a report dict."""
    g=canvas.g; h,w=g.shape
    ship=canvas.ship_mask()
    n_tiles=int(ship.sum())
    # candidate node positions = backbone tiles that are also ship tiles
    cand=[(int(x),int(y)) for y in range(h) for x in range(w)
          if canvas.bb[y,x] and ship[y,x]]
    if not cand:
        return dict(tiles=n_tiles, covered=0, cover_pct=0.0, placements=[],
                    chain_ok=False, liftable=False, max_dist=None,
                    note="no backbone/ship candidates")
    cand_arr=np.array(cand)               # (K,2) x,y
    # precompute engine/ext disks lazily
    def cover_of(cx,cy,r):
        return _disk_mask(h,w,cx,cy,r) & ship

    # 1) engine: pick backbone tile whose r19 disk covers the most ship tiles
    best=None
    for (cx,cy) in cand:
        c=int(cover_of(cx,cy,R_ENG).sum())
        if best is None or c>best[0]:
            best=(c,cx,cy)
    _,ex,ey=best
    field=cover_of(ex,ey,R_ENG)
    placements=[('ENGINE',ex,ey,R_ENG)]

    # 2) up to N_EXT extenders: each must sit on a currently-covered backbone
    #    tile, chosen to add the most newly-covered ship tiles. Stop early once
    #    everything is covered (so we can report how MANY extenders are needed).
    chain_ok=True
    for _ in range(N_EXT):
        if int((field & ship).sum())>=n_tiles:      # already fully covered
            break
        best=None
        for (cx,cy) in cand:
            if not field[cy,cx]:            # chain rule: must be inside field
                continue
            newcov=cover_of(cx,cy,R_EXT) & ~field
            gain=int(newcov.sum())
            if best is None or gain>best[0]:
                best=(gain,cx,cy)
        if best is None or best[0]==0:      # nothing legal or nothing to gain
            if best is None: chain_ok=False
            break
        _,cx,cy=best
        field=field | cover_of(cx,cy,R_EXT)
        placements.append(('EXT',cx,cy,R_EXT))

    n_ext_used=len(placements)-1
    covered=int((field & ship).sum())
    uncovered=n_tiles-covered
    # farthest ship tile from any node (diagnostic)
    ys,xs=np.where(ship)
    nodes=np.array([(p[1],p[2]) for p in placements])
    d=np.sqrt(((xs[:,None]-nodes[:,0][None,:])**2 +
               (ys[:,None]-nodes[:,1][None,:])**2)).min(axis=1)
    max_dist=float(d.max())
    liftable = (n_tiles<=CAP) and (uncovered==0) and chain_ok and (n_ext_used<=N_EXT)
    return dict(tiles=n_tiles, cap=CAP, headroom=CAP-n_tiles,
                covered=covered, uncovered=uncovered,
                cover_pct=round(100*covered/max(1,n_tiles),2),
                placements=placements, n_ext_used=n_ext_used, n_ext_max=N_EXT,
                r_eng=R_ENG, r_ext=R_EXT, chain_ok=chain_ok,
                max_dist=round(max_dist,2), liftable=bool(liftable))

# ---- zone tally ---------------------------------------------------------
def tally(canvas):
    vals,counts=np.unique(canvas.g,return_counts=True)
    return {v:int(c) for v,c in zip(vals,counts) if v!=''}
