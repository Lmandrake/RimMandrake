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
import math
import numpy as np, json, math

# ---- VANILLA limits (kept for reference) --------------------------------
VAN_R_ENG, VAN_R_EXT, VAN_CAP, VAN_N_EXT = 19, 16, 2000, 6

# ---- EXPANDED limits (Bigger Gravships, APPROVED 2026-08-06) -------------
# ✅ NO LONGER ASSUMED. This block used to say "generous ASSUMED values pending
# the real slider ranges (Fetcher 2026-08-06_bigger_gravships_ranges)" while its
# own footer said they were read from the stored floats. Both halves were in the
# file at once. Verified offline 2026-08-13 (a retired seat, queue C4): all four match
# the config exactly, so the ASSUMED framing is retired, not just amended.
#
# ⚠️ DO NOT "verify" THESE AGAINST THE DEF. They will not match and are not
# meant to. Three layers write these fields, last writer wins:
#   1. Odyssey XML  GravFieldExtender radius 16.9, GravEngine footprint 18.9
#   2. Vanilla Gravship Expanded (vanillaexpanded.gravship) patches them DOWN
#      to 12.9 / 11.9
#   3. Bigger Gravships (redmattis.biggergravship) ships NO XML -- it stamps
#      these into the comps from C# during implied-def generation, which runs
#      after all XML patching, so it wins regardless of load order.
# So the numbers below exist only as stored floats plus a Harmony prefix. The
# def literals on disk DISAGREE with this file, correctly.
#
# ⚠️ THESE ARE MOD SETTINGS, NOT DEFAULTS, AND THE SHIP FLIES ONLY WITH THEM.
# Set by the owner 2026-08-13 and verified from the STORED FLOATS, not the UI:
#   file:///C:/Users/Mandrake/AppData/LocalLow/Ludeon%20Studios/RimWorld%20by%20Ludeon%20Studios/Config/Mod_3522759531_GravshipSizeSettings.xml
#     BG_gravEngineMaxDistance             34
#     BG_gravExtenderMaxDistance           30
#     BG_gravExtenderMax                   12
#     BG_gravExtenderMaxDistanceFromEngine 85
# Bigger Gravships' own DEFAULTS are 25.9 / 25.9 / 8 / 25.9, and at those the
# hull does not lift at all -- no extender layout can cover it (measured: needs
# a reach of 74.46, defaults give 51.80). So if that config file is lost or the
# owner clicks "Restore Mod Defaults", this design silently stops being
# liftable. Nothing logs it.
#
# Read the FILE, never the settings panel: the panel renders 25.9 as "26", and
# only NON-DEFAULT values are written, so an absent key means default, not zero.
R_ENG   = 34     # grav engine connection radius   (vanilla 19, BG default 25.9)
R_EXT   = 30     # field extender connection radius (vanilla 16, BG default 25.9)
N_EXT   = 12     # max field extenders             (vanilla 6,  BG default 8)
D_MAX   = 85     # max extender distance FROM THE ENGINE (BG default 25.9)

# Substructure support. ⚠️ THE TWO NUMBERS HAVE DIFFERENT PROVENANCE -- this
# comment used to claim both came "from the same settings file" and that was
# wrong for the second one (a retired seat, 2026-08-13, queue C4):
#   ENG_SUPPORT  IS in the config: BG_gravEngineSupport = 632.79541
#   EXT_SUPPORT  is NOT in the config. There is no BG_gravExtenderSupport key.
#                500 is Bigger Gravships' compiled MOD DEFAULT.
# It is the right value, and it was believed for the wrong reason. That mattered:
# had the effective figure instead been VGE's 100 or vanilla's 250, CAP would be
# 1832.8 or 3632.8 -- BELOW the 4,057-tile hull -- and the ship would have failed
# on CAPACITY, with the radius work all correct and looking for the bug.
# The old flat CAP=4800 was an assumption and was wrong; it never bound.
ENG_SUPPORT = 632.8
EXT_SUPPORT = 500
CAP     = int(ENG_SUPPORT + EXT_SUPPORT * N_EXT)   # 6632

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
    def arc(self, cx, cy, r, deg0, deg1, half, code, backbone=True,
            only_empty=False):
        """A CURVED corridor: walk the angular span deg0->deg1 at radius r,
        stamping a (2*half+1) square brush at each step so the path is a smooth
        arc, never straight. Lays backbone on the centerline by default so the
        verifier can chain engine/extenders along the curve. deg1 may exceed 360
        or be < deg0 (it sweeps the short way round in the given direction)."""
        a0=math.radians(deg0); a1=math.radians(deg1)
        steps=max(2,int(abs(a1-a0)*r)+1)
        for t in np.linspace(0,1,steps):
            a=a0+(a1-a0)*t
            xi=int(round(cx+r*math.cos(a))); yi=int(round(cy+r*math.sin(a)))
            for dy in range(-half,half+1):
                for dx in range(-half,half+1):
                    x,y=xi+dx,yi+dy
                    if 0<=y<self.h and 0<=x<self.w:
                        if only_empty and self.g[y,x]!='': continue
                        self.g[y,x]=code
            if backbone and 0<=yi<self.h and 0<=xi<self.w:
                self.bb[yi,xi]=True
    def line_backbone(self, x0,y0,x1,y1):
        """Lay backbone (only) along a straight segment — no tiles painted."""
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        for xf,yf in zip(np.linspace(x0,x1,n),np.linspace(y0,y1,n)):
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

def _count_components(ship):
    """Number of 4-connected components of the ship mask. A real gravship must
    be ONE contiguous structure (all parts touch), so a liftable design needs
    exactly 1. BFS flood fill over the boolean mask."""
    h,w=ship.shape
    seen=np.zeros_like(ship,dtype=bool)
    comps=0; biggest=0
    for sy in range(h):
        for sx in range(w):
            if ship[sy,sx] and not seen[sy,sx]:
                comps+=1; size=0
                stack=[(sy,sx)]; seen[sy,sx]=True
                while stack:
                    y,x=stack.pop(); size+=1
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=y+dy,x+dx
                        if 0<=ny<h and 0<=nx<w and ship[ny,nx] and not seen[ny,nx]:
                            seen[ny,nx]=True; stack.append((ny,nx))
                biggest=max(biggest,size)
    return comps,biggest

def place_and_verify(canvas):
    """Greedily place engine + 6 extenders on the backbone to maximise
    coverage of ship tiles, obeying the chain rule. Returns a report dict."""
    g=canvas.g; h,w=g.shape
    ship=canvas.ship_mask()
    n_tiles=int(ship.sum())
    n_components,biggest_comp=_count_components(ship)
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
            # ⚠️ THE CONSTRAINT THIS SOLVER USED TO IGNORE ENTIRELY. Bigger
            # Gravships caps how far an extender may sit FROM THE ENGINE,
            # separately from any radius. Without this the solver happily
            # produced a layout whose worst extender sat 84.72 out -- legal only
            # because the owner later set the cap to 85, a margin of 0.28 cells.
            if math.hypot(cx-ex, cy-ey) > D_MAX:
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
    # worst extender distance from the engine, and what is left of the cap
    ext_d=[math.hypot(p[1]-ex, p[2]-ey) for p in placements[1:]]
    worst_ext_d=max(ext_d) if ext_d else 0.0
    d_margin=D_MAX-worst_ext_d
    covered=int((field & ship).sum())
    uncovered=n_tiles-covered
    # farthest ship tile from any node (diagnostic)
    ys,xs=np.where(ship)
    nodes=np.array([(p[1],p[2]) for p in placements])
    d=np.sqrt(((xs[:,None]-nodes[:,0][None,:])**2 +
               (ys[:,None]-nodes[:,1][None,:])**2)).min(axis=1)
    max_dist=float(d.max())
    contiguous = (n_components==1)
    liftable = (n_tiles<=CAP) and (uncovered==0) and chain_ok \
               and (n_ext_used<=N_EXT) and contiguous \
               and (worst_ext_d<=D_MAX)
    return dict(tiles=n_tiles, cap=CAP, headroom=CAP-n_tiles,
                covered=covered, uncovered=uncovered,
                cover_pct=round(100*covered/max(1,n_tiles),2),
                placements=placements, n_ext_used=n_ext_used, n_ext_max=N_EXT,
                r_eng=R_ENG, r_ext=R_EXT, d_max=D_MAX,
                worst_ext_dist=round(worst_ext_d,2),
                d_margin=round(d_margin,2), chain_ok=chain_ok,
                n_components=n_components, biggest_comp=biggest_comp,
                contiguous=bool(contiguous),
                max_dist=round(max_dist,2), liftable=bool(liftable))

# ---- zone tally ---------------------------------------------------------
def tally(canvas):
    vals,counts=np.unique(canvas.g,return_counts=True)
    return {v:int(c) for v,c in zip(vals,counts) if v!=''}
