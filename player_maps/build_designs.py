"""Build the EXPANDED candidate topologies (Bigger Gravships limits),
verify each, ENFORCE the full region set, save grids + report.

FULL required region set (from ship_deck_plan.md — checked, not assumed).
Every design must contain ALL of these, or the build prints FAIL:
  systems : M command · S thrusters+power · U fuel · W water · H shuttle bay
  factory : A raw-extraction · B bulk/dirty · C food · D textile/ammo ·
            E advanced-materials · F precision      (all six Factory_lore wings)
  storage : G cargo hold
  living  : R habitat
  luxury  : T carbonite bay

CHANGELOG 2026-08-06 (user pass):
  - Added SHUTTLE BAY (H) as a 14th mandatory region.
  - Removed the two triangular Imperial-military designs (Star Destroyer wedge,
    Manta delta) — reserved for Imperial ships, not this Jawa hulk.
  - Added #7 NODAL STATION: two central nuclei (cargo + carbonite) each
    radiating asymmetric spoke-corridors to exterior octagon "cells" (one per
    factory wing / water / habitat / command), shuttle dock on the longest
    spoke. Every spoke is 5 wide = belt-in + belt-out + walking lane.
"""
import numpy as np, json, math
from ship_designs import Canvas, place_and_verify, tally, CAP, R_ENG, R_EXT, N_EXT

REQUIRED = set('MSUWH' 'ABCDEF' 'G' 'R' 'T')   # 14 regions, all mandatory now

designs = {}

# =====================================================================
# 1 · SPINAL FREIGHTER  (long keel, production wings, all regions)
# =====================================================================
def d_freighter():
    c=Canvas(56,168); cx=28; HW=15
    c.rect(cx-2,12,cx+2,158,'K'); c.backbone_rect(cx,12,cx,158)
    c.rect(cx-12,2,cx+12,11,'M')                         # command bow
    def wing(y0,y1,l,r):
        c.rect(cx-3,y0,cx-HW,y1,l); c.rect(cx+3,y0,cx+HW,y1,r)
    wing(13,30,'F','E')     # precision / adv-mat (HOT outboard)
    wing(33,50,'G','G')     # CARGO band 1
    wing(53,70,'C','B')     # food / bulk (HOT)
    wing(73,90,'D','A')     # textile-ammo / raw extraction
    wing(93,110,'R','R')    # habitat
    wing(113,130,'G','H')   # cargo band 2 (port) / SHUTTLE BAY (starboard)
    wing(133,150,'W','U')   # water / fuel
    c.rect(cx-12,151,cx+12,158,'S')                      # stern thrusters/power
    c.rect(cx-6,159,cx+6,164,'T')                        # carbonite tail
    c.crop(); return c
designs['1_spinal_freighter']=d_freighter()

# =====================================================================
# 2 · NEBULON-B FRIGATE  (forward hull + thin neck + rear hull)
# =====================================================================
def d_nebulonb():
    c=Canvas(60,158); cx=30
    c.disk(cx,28,18,'G')
    c.ring(cx,28,18,13,'R')          # outer forward = habitat
    c.disk(cx,28,8,'M')              # command core
    c.rect(cx-16,32,cx+16,44,'F')    # forward underside: precision hangar bay
    # neck carries the small-footprint regions so they all fit
    c.rect(cx-3,45,cx+3,96,'K')
    c.rect(cx-9,45,cx+9,51,'H')      # SHUTTLE BAY on the neck (dorsal dock)
    c.rect(cx-9,52,cx+9,60,'C')      # mess (food)
    c.rect(cx-9,62,cx+9,70,'D')      # textile/ammo pod
    c.rect(cx-9,72,cx+9,80,'W')      # water pod
    c.rect(cx-9,82,cx+9,90,'A')      # raw-extraction pod (drill drones)
    c.rect(cx,10,cx,146,'K'); c.backbone_rect(cx,12,cx,144)
    # rear engineering hull
    c.rect(cx-16,97,cx+16,144,'E')   # adv-materials engineering block (HOT)
    c.rect(cx-16,97,cx-5,144,'G')    # port side cargo
    c.rect(cx+5,110,cx+16,126,'B')   # starboard bulk (HOT)
    c.rect(cx-16,128,cx-5,144,'U')   # fuel bunkerage
    c.rect(cx+5,128,cx+16,140,'T')   # carbonite vault in the aft hull
    c.rect(cx-13,145,cx+13,152,'S')  # engine bank
    c.crop(); return c
designs['2_nebulon_b']=d_nebulonb()

# =====================================================================
# 3 · CORELLIAN CORVETTE  (hammerhead bow, engine cluster aft)
# =====================================================================
def d_corvette():
    c=Canvas(60,150); cx=30
    c.disk(cx,22,20,'M'); c.carve(cx-20,0,cx+20,6)
    c.ring(cx,22,20,14,'R')          # around the head: habitat
    c.disk(cx,22,9,'M')              # bridge core
    c.taper(cx,42,120,18,11,'G')     # body = cargo, narrowing aft
    c.rect(cx,8,cx,130,'K'); c.backbone_rect(cx,10,cx,128)
    # body bands (all six factory wings + tanks stacked down the body)
    c.rect(cx-16,44,cx-4,58,'F'); c.rect(cx+4,44,cx+16,58,'E')   # precision / advmat(HOT)
    c.rect(cx-15,60,cx-4,74,'A'); c.rect(cx+4,60,cx+15,74,'B')   # raw / bulk(HOT)
    c.rect(cx-14,76,cx-4,90,'C'); c.rect(cx+4,76,cx+14,90,'D')   # food / textile-ammo
    c.rect(cx-13,92,cx-4,110,'W'); c.rect(cx+4,92,cx+13,110,'U') # water / fuel
    c.rect(cx-13,112,cx+13,118,'H')                             # SHUTTLE BAY (wide aft-body dock)
    c.rect(cx-3,108,cx+3,111,'T')                               # carbonite vault (compact)
    c.rect(cx-11,119,cx+11,121,'S')                             # stern thruster deck (ties fins to body)
    for dx in (-10,-5,0,5,10):                                  # tail engine cluster
        c.rect(cx+dx-1,120,cx+dx+1,132,'S')                     # fins overlap the deck (contiguous)
    c.crop(); return c
designs['3_corellian_corvette']=d_corvette()

# =====================================================================
# 4 · CATAMARAN COURTYARD  (twin hull + open courts)
# =====================================================================
def d_catamaran():
    c=Canvas(70,138); cx=35
    xL,xR=cx-13,cx+13; court_half=7
    y0,y1=14,116
    c.rect(xL-9,y0,xL+6,y1,'G'); c.rect(xR-6,y0,xR+9,y1,'G')     # two hull cores
    c.rect(xL,y0,xL,y1,'K'); c.backbone_rect(xL,y0+2,xL,y1-2)
    c.rect(xR,y0,xR,y1,'K'); c.backbone_rect(xR,y0+2,xR,y1-2)
    c.rect(xL-9,5,xR+9,13,'M'); c.backbone_rect(xL,8,xR,8)       # bow command cross-deck (reaches hull row 14)
    c.rect(xL-9,117,xR+9,125,'S'); c.backbone_rect(xL,121,xR,121) # stern thruster deck
    # PORT hull = the four "clean" factory wings + habitat + water + shuttle
    a,b=xL-9,xL+6
    c.rect(a,y0,b,y0+12,'F'); c.rect(a,y0+14,b,y0+26,'D')        # precision / textile-ammo
    c.rect(a,72,b,84,'C');    c.rect(a,86,b,98,'R')            # food / habitat
    c.rect(a,100,b,108,'W');  c.rect(a,109,b,y1,'H')           # water / SHUTTLE BAY
    # STARBOARD hull = the HOT + extraction wings + fuel + carbonite
    a,b=xR-6,xR+9
    c.rect(a,y0,b,y0+12,'E'); c.rect(a,y0+14,b,y0+26,'B')        # advmat(HOT) / bulk(HOT)
    c.rect(a,72,b,84,'A');    c.rect(a,86,b,98,'R')            # raw extraction / habitat
    c.rect(a,100,b,y1-8,'U'); c.rect(a,y1-6,b,y1,'T')          # fuel / carbonite
    # central catwalk carries backbone amidships; splits open area into 2 courts
    c.rect(cx,y0,cx,y1,'.'); c.backbone_rect(cx,y0+1,cx,y1-1)
    c.rect(cx-7,58,cx+7,64,'.'); c.backbone_rect(cx-7,61,cx+7,61)
    c.carve(cx-court_half,16,cx+court_half,56)                   # fore court
    c.carve(cx-court_half,66,cx+court_half,114)                  # aft court
    c.rect(cx,16,cx,114,'.'); c.backbone_rect(cx,17,cx,113)
    c.crop(); return c
designs['4_catamaran_courtyard']=d_catamaran()

# =====================================================================
# 5 · RING STATION  (annulus around a large central hangar)
# =====================================================================
def d_ring():
    c=Canvas(104,104); cx=cy=50; Rout=46; Rin=26
    c.ring(cx,cy,Rout,Rin,'G')
    mid=(Rout+Rin)//2
    yy,xx=np.mgrid[0:c.h,0:c.w]; d2=(xx-cx)**2+(yy-cy)**2
    band=(d2<=(mid+1)**2)&(d2>=(mid-1)**2)&(c.g!='')
    c.bb[band]=True; c.g[band]='K'
    ang=np.arctan2(yy-cy,xx-cx); ringmask=(d2<=Rout*Rout)&(d2>=Rin*Rin)
    def wedge(a0,a1,code):
        m=ringmask&(ang>=a0)&(ang<a1)&(c.g!='K'); c.g[m]=code
    # 8 arc sectors around the ring cover all six factory wings + cargo/habitat
    step=2*math.pi/8
    codes=['F','E','A','B','C','D','G','R']       # 8 arcs
    for i,code in enumerate(codes):
        a0=-math.pi+i*step; wedge(a0,a0+step,code)
    # four cardinal system blocks over the keel band (kept, they overwrite arcs locally)
    c.rect(cx-4,cy-Rout,cx+4,cy-Rout+9,'S')      # N thrusters
    c.rect(cx-4,cy+Rin,cx+4,cy+Rout,'W')          # S water
    c.rect(cx-Rout,cy-4,cx-Rin,cy+4,'U')          # W fuel
    c.rect(cx+Rin,cy-4,cx+Rout,cy+4,'M')          # E command
    c.rect(cx-3,cy-Rout+10,cx+3,cy-Rout+16,'T')   # carbonite just inside N
    # SHUTTLE BAY: a docking blister on the outer hull (NE), tethered by a stub
    c.rect(cx+28,cy-28,cx+34,cy-22,'.'); c.backbone_rect(cx+28,cy-28,cx+34,cy-22) # stub
    c.octagon(cx+40,cy-30,7,'H'); c.backbone_rect(cx+40,cy-30,cx+40,cy-30)        # external dock
    c.crop(); return c
designs['5_ring_station']=d_ring()

# =====================================================================
# 6 · SALVAGE HULK  (asymmetric — one grand wing, one broken stub)
# =====================================================================
def d_hulk():
    c=Canvas(80,132); spine=34
    c.rect(spine-2,8,spine+2,120,'K'); c.backbone_rect(spine,8,spine,120)
    c.rect(spine-9,2,spine+9,7,'M')                      # command bow
    # PORT side (left): full, long, richly built  (width kept <=25 for r30)
    def port(y0,y1,code): c.rect(spine-3,y0,spine-25,y1,code)
    port(9,26,'F'); port(29,46,'G'); port(49,64,'C')
    port(67,82,'D'); port(85,100,'R'); port(103,116,'W')
    # STARBOARD side (right): a short, jagged, half-rebuilt stub
    c.rect(spine+3,9,spine+20,26,'E')                    # working adv-mat wing (HOT)
    c.rect(spine+3,29,spine+15,44,'G')                   # cargo stub
    c.rect(spine+3,47,spine+11,60,'B')                   # bulk stub (HOT)
    c.rect(spine+3,63,spine+18,80,'H')                   # SHUTTLE BAY rebuilt in the gap
    c.rect(spine+3,87,spine+18,102,'U')                  # fuel stub near stern
    c.rect(spine+3,104,spine+14,116,'T')                 # carbonite vault in the stub
    c.rect(spine-9,121,spine+16,128,'S')                 # asymmetric stern thrusters
    # a small satellite pod off the port bow (tethered by keel stub)
    c.rect(spine-25,15,spine-19,15,'K'); c.backbone_rect(spine-25,15,spine-19,15)
    c.rect(spine-32,10,spine-24,24,'A')                  # raw-extraction pod
    c.crop(); return c
designs['6_salvage_hulk']=d_hulk()

# =====================================================================
# 7 · NODAL STATION  (two central nuclei radiating asymmetric spokes)
#   Inspired by the reference image: octagon "hub" nodes joined by
#   window-lined corridor spokes. Two nuclei — CARGO (G) and CARBONITE (T) —
#   each throw spokes out to exterior octagon CELLS, one per function.
#   Every spoke is 5 tiles wide: belt-in + belt-out + a central walking lane.
#   The shuttle bay (H) sits on the LONGEST spoke, extended well past the rest.
# =====================================================================
def d_nodal():
    c=Canvas(160,150)
    N1=(62,66)    # CARGO nucleus
    N2=(86,74)    # CARBONITE nucleus
    # exterior cells fed by the CARGO nucleus (supply / clean side)
    n1_nodes=[(50,38,'M'),(74,32,'C'),(34,54,'F'),(32,84,'E'),
              (46,104,'W'),(70,112,'A')]
    # exterior cells fed by the CARBONITE nucleus (hot / heavy side + dock)
    n2_nodes=[(102,34,'D'),(116,54,'B'),(120,82,'U'),
              (106,108,'R'),(84,116,'S'),(140,66,'H')]   # H = shuttle, longest spoke
    allnodes=n1_nodes+n2_nodes
    # 1) spokes first (thick grey corridors, backbone laid on centerline)
    for (x,y,_) in n1_nodes: c.spoke(N1[0],N1[1],x,y,2,'.')
    for (x,y,_) in n2_nodes: c.spoke(N2[0],N2[1],x,y,2,'.')
    c.spoke(N1[0],N1[1],N2[0],N2[1],2,'.')              # inter-nucleus link
    # 2) nuclei octagons (drawn over spoke roots)
    c.octagon(*N1,10,'G'); c.backbone_rect(N1[0],N1[1],N1[0],N1[1])
    c.octagon(*N2,10,'T'); c.backbone_rect(N2[0],N2[1],N2[0],N2[1])
    # 3) exterior cell octagons (drawn over spoke tips). Shuttle bay larger.
    for (x,y,code) in allnodes:
        r=10 if code=='H' else 7
        c.octagon(x,y,r,code); c.backbone_rect(x,y,x,y)
    c.crop(); return c
designs['7_nodal_station']=d_nodal()

# =====================================================================
# 8 · RING-AND-SPUR  (ring core + semi-random circular pods on spokes)
#   Hybrid of #5 Ring and #7 Nodal: a THINNER main ring carries the core
#   systems (cargo body + command/thrusters/water/fuel/carbonite on the band),
#   and eight CIRCULAR PODS burst outward on 5-wide spokes at jittered angles,
#   deliberately breaking the ring's symmetry. Each pod = one function (the six
#   factory wings + habitat + shuttle). One pod (shuttle H) is LARGER and thrown
#   further out. Angles/offsets are fixed-but-irregular ("semi-random" look,
#   deterministic so the build reproduces).
# =====================================================================
def d_ring_spur():
    c=Canvas(160,160); cx=cy=80
    Rout=34; Rin=22; Rmid=(Rout+Rin)//2          # ring band 22..34, midline 28
    c.ring(cx,cy,Rout,Rin,'G')                   # ring body = cargo
    # keel on the ring midline (full circle backbone)
    yy,xx=np.mgrid[0:c.h,0:c.w]; d2=(xx-cx)**2+(yy-cy)**2
    band=(d2<=(Rmid+1)**2)&(d2>=(Rmid-1)**2)&(c.g!='')
    c.bb[band]=True; c.g[band]='K'
    # core system blocks over the ring band (they keep the keel mask beneath)
    c.rect(cx-4,cy-Rout,cx+4,cy-Rin,'S')         # top thrusters + power
    c.rect(cx-4,cy+Rin,cx+4,cy+Rout,'W')         # bottom water tanks
    c.rect(cx-Rout,cy-4,cx-Rin,cy+4,'U')         # left fuel bunkerage
    c.rect(cx+Rin,cy-4,cx+Rout,cy+4,'M')         # right command / control
    ta=math.radians(45)                          # carbonite vault tucked on the band
    tx=int(cx+Rmid*math.cos(ta)); ty=int(cy+Rmid*math.sin(ta))
    c.rect(tx-3,ty-3,tx+3,ty+3,'T')
    # eight circular pods at jittered angles (deg, radial offset past midline,
    # pod radius, code). Shuttle H is bigger and flung further out.
    pods=[( 15,18, 7,'F'),( 68,22, 7,'E'),(110,16, 7,'A'),(150,24, 7,'B'),
          (196,19, 7,'C'),(238,15, 7,'D'),(300,20, 7,'R'),(340,26,10,'H')]
    for (deg,out,pr,code) in pods:
        a=math.radians(deg)
        ox=cx+Rout*math.cos(a);        oy=cy+Rout*math.sin(a)          # ring attach
        px=cx+(Rmid+out)*math.cos(a);  py=cy+(Rmid+out)*math.sin(a)    # pod centre
        c.spoke(ox,oy,px,py,2,'.')                                     # 5-wide spoke
        c.disk(int(round(px)),int(round(py)),pr,code)                  # the ball
        c.backbone_rect(int(round(px)),int(round(py)),int(round(px)),int(round(py)))
    c.crop(); return c
designs['8_ring_spur']=d_ring_spur()

# =====================================================================
# 9 · DERELICT HALO  (ring + free-floating bulbs + curved perimeter walks)
#   The eerie variant. A main ring carries the core systems. Circular PODS
#   float outboard at jittered angles/distances but are NOT joined to the ring
#   by any radial spoke — they simply hang there. Instead, "strange" CURVED
#   perimeter walkways arc around the OUTSIDE of the hull, some overshooting a
#   little past everything into empty space for reasons long forgotten. Nothing
#   is straight. The interior is a hollow void EXCEPT a single arcing causeway
#   that curves inward to the ship's heart: the GRAV ENGINE core, ringed by a
#   small consecrated floor bearing the Jawa's worshipful scrap totems (T).
#   (Field coverage, not corridors, keeps the floating pods liftable.)
# =====================================================================
def _spiral(c, cx, cy, r0, r1, a_deg, sweep_deg, half, code, backbone=True):
    """A CURVED tether: radius eases r0->r1 while the angle sweeps, tracing an
    arc/spiral (never a straight radial line). Stamps a (2*half+1) brush so it
    stays 4-connected, and overlaps whatever sits at r0 and r1 (so it physically
    JOINS them). Returns the (x,y) of the far end."""
    a0=math.radians(a_deg); span=math.radians(sweep_deg)
    steps=max(4,int(abs(r1-r0)+abs(span)*max(r0,r1))+1)
    ex=ey=0
    for t in np.linspace(0,1,steps):
        r=r0+(r1-r0)*t; a=a0+span*t
        xi=int(round(cx+r*math.cos(a))); yi=int(round(cy+r*math.sin(a)))
        c.rect(xi-half,yi-half,xi+half,yi+half,code)
        if backbone and 0<=yi<c.h and 0<=xi<c.w: c.bb[yi,xi]=True
        ex,ey=xi,yi
    return ex,ey

def d_halo():
    c=Canvas(210,210); cx=cy=105
    Rin=24; Rout=34; Rmid=(Rin+Rout)//2          # main ring band 24..34
    c.ring(cx,cy,Rout,Rin,'G')                   # ring body = cargo
    yy,xx=np.mgrid[0:c.h,0:c.w]; d2=(xx-cx)**2+(yy-cy)**2
    band=(d2<=(Rmid+1)**2)&(d2>=(Rmid-1)**2)&(c.g!='')
    c.bb[band]=True; c.g[band]='K'               # keel on ring midline
    # core systems set into the ring band (four cardinals)
    c.rect(cx-4,cy-Rout,cx+4,cy-Rin,'S')         # top   thrusters + power
    c.rect(cx-4,cy+Rin,cx+4,cy+Rout,'W')         # bottom water tanks
    c.rect(cx-Rout,cy-4,cx-Rin,cy+4,'U')         # left  fuel bunkerage
    c.rect(cx+Rin,cy-4,cx+Rout,cy+4,'M')         # right command / control
    # ---- the hollow heart: grav-engine core + consecrated totem floor -------
    c.disk(cx,cy,6,'.')                          # consecrated floor (scrap shrine)
    c.rect(cx-2,cy-2,cx+2,cy+2,'T')              # the worshipful scrap totems / relic core
    c.backbone_rect(cx-6,cy-6,cx+6,cy+6)         # engine may seat here (ship's heart)
    # ---- single arcing causeway: ring inner edge -> the core ----------------
    # a curved path (constant-ish sweep, radius easing inward), never straight.
    # r0=Rmid (23) so it overlaps the keel band and JOINS ring->core physically.
    a_start=math.radians(300)                    # springs from the ring low-right
    segs=64
    for t in np.linspace(0,1,segs):
        r=Rmid-(Rmid-3)*t                        # ease from ring band (28) to core (3)
        a=a_start+math.radians(150)*t            # sweep 150 deg as it descends
        xi=int(round(cx+r*math.cos(a))); yi=int(round(cy+r*math.sin(a)))
        c.rect(xi-1,yi-1,xi+1,yi+1,'.')          # 3-wide causeway
        c.bb[yi,xi]=True                         # backbone along the causeway
    # ---- pods on CURVED tethers (arc/spiral, never a straight radial spoke) --
    # Every pod is joined to the ring by a curved tether that eases from the ring
    # band out to the pod (they physically TOUCH — a gravship is one contiguous
    # structure). The tethers sweep, so they read as "strange curved walkways",
    # not clean spokes. (deg, pod-centre radius, pod radius, tether-sweep deg, code)
    pods=[( 22,46, 7, 34,'F'),( 63,50, 7,-30,'E'),(107,44, 7, 30,'A'),
          (148,52, 7,-28,'B'),(196,47, 7, 32,'C'),(243,45, 7,-30,'D'),
          (292,49, 7, 30,'R'),(334,62,10,-26,'H')]   # shuttle bigger, furthest
    pod_ctr={}
    for (deg,pod_r,pr,sweep,code) in pods:
        # curved tether: ring band (r=Rmid) -> pod centre, sweeping `sweep` deg
        _spiral(c,cx,cy, Rmid, pod_r, deg-sweep, sweep, 1, '.')
        a=math.radians(deg)
        px=int(round(cx+pod_r*math.cos(a))); py=int(round(cy+pod_r*math.sin(a)))
        c.disk(px,py,pr,code)                    # the ball (drawn over tether tip)
        c.backbone_rect(px,py,px,py)
        pod_ctr[code]=(px,py,pod_r,deg,pr)
    # ---- strange perimeter walks that OVERSHOOT past the hull "for mysterious
    #      reasons" — but each is ANCHORED to a pod (starts on the pod, arcs
    #      outward into empty space), so it's part of the ship, not debris. -----
    for code,extra_sweep,extra_reach in [('H',40,10),('R',34,8),('E',-30,7)]:
        px,py,pod_r,deg,pr=pod_ctr[code]
        # begin just inside the pod edge, spiral outward beyond it and dangle off
        _spiral(c,cx,cy, pod_r-pr+1, pod_r+extra_reach, deg, extra_sweep, 1, '.')
    c.crop(); return c
designs['9_derelict_halo']=d_halo()

# =====================================================================
report={}
for name,c in designs.items():
    rep=place_and_verify(c)
    z=tally(c); rep['zones']=z
    have=set(z.keys())
    missing=sorted(REQUIRED-have)
    rep['missing_required']=missing
    np.save(f'design_{name}.npy', c.g); np.save(f'design_{name}_bb.npy', c.bb)
    json.dump([list(p) for p in rep['placements']], open(f'design_{name}_place.json','w'))
    report[name]=rep
    flag='OK' if (rep['liftable'] and not missing) else 'FAIL'
    print(f"[{flag}] {name:22s} tiles={rep['tiles']:4d}/{CAP} ext={rep['n_ext_used']}/{N_EXT} "
          f"cov={rep['cover_pct']}% uncov={rep['uncovered']} parts={rep['n_components']} "
          f"maxd={rep['max_dist']} lift={rep['liftable']} missing={missing}")
json.dump(report, open('designs_report.json','w'), indent=1, default=str)
print(f"\nrequired regions ({len(REQUIRED)}): {''.join(sorted(REQUIRED))}")
print(f"limits: R_ENG={R_ENG} R_EXT={R_EXT} CAP={CAP} N_EXT={N_EXT}")
print("saved all grids + designs_report.json")
