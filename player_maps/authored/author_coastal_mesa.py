#!/usr/bin/env python3
"""
author_coastal_mesa.py  —  LLM-AUTHORED RimWorld map (no heuristic engine).

Every region boundary, coastline curve, gradient, and set-piece position in
this file was DECIDED BY REASONING and written as explicit coordinates. Cairo
is only the pen: it draws exactly the shapes specified here. There is no
algorithm choosing what/where — the map designer (the LLM) is.

Two panels:
  BEFORE  — the plain "player map": straight coast, blank sand flat, plain mesa.
  AFTER   — the same bones, improved: meandering coast w/ headland+cove+sandbar,
            depth-graded water, a dry wash feeding a fertile hollow, scrub,
            an outcrop knoll, a cave carved into the massif, plus five exotic
            hand-placed set-pieces (crashed Factory-ship scar, abandoned mine,
            semi-working refinery, dead droid in an impact crater, cavern).
"""
import cairo, math, random

# ------------------------------------------------------------------ palette
COL = {
    "deep":    (0.086, 0.216, 0.267),
    "shallow": (0.157, 0.396, 0.451),
    "beach":   (0.760, 0.680, 0.500),
    "sand":    (0.851, 0.769, 0.560),
    "sand_hi": (0.886, 0.812, 0.612),
    "sand_lo": (0.796, 0.706, 0.500),
    "soil":    (0.404, 0.318, 0.208),
    "soil_rich":(0.322,0.243, 0.145),
    "gravel":  (0.659, 0.596, 0.478),
    "scree":   (0.541, 0.498, 0.427),
    "rock":    (0.435, 0.412, 0.376),
    "rock_hi": (0.510, 0.482, 0.435),
    "rock_lo": (0.298, 0.278, 0.247),
    "cave":    (0.180, 0.165, 0.145),
    "scrub":   (0.353, 0.427, 0.220),
    "scrub_hi":(0.451, 0.525, 0.290),
    "fertile": (0.263, 0.325, 0.161),
    "concrete":(0.604, 0.580, 0.529),
    "metal":   (0.357, 0.376, 0.408),
    "metal_hi":(0.478, 0.498, 0.529),
    "rust":    (0.451, 0.294, 0.180),
    "scorch":  (0.118, 0.106, 0.098),
    "ink":     (0.09, 0.09, 0.10),
}
def rgb(n): return COL[n]

W = H = 760  # per panel

# ------------------------------------------------------------------ helpers
def catmull(ctx, pts, closed=False):
    """Smooth path through pts via Catmull-Rom -> bezier. Points are (x,y)."""
    p = list(pts)
    if closed:
        p = [p[-1]] + p + [p[0], p[1]]
    else:
        p = [p[0]] + p + [p[-1]]
    ctx.move_to(*p[1])
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        c1 = (p1[0] + (p2[0]-p0[0])/6.0, p1[1] + (p2[1]-p0[1])/6.0)
        c2 = (p2[0] - (p3[0]-p1[0])/6.0, p2[1] - (p3[1]-p1[1])/6.0)
        ctx.curve_to(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        ctx.close_path()

def blobpath(ctx, cx, cy, rx, ry, seed, wobble=0.22, n=11):
    """Irregular closed organic blob around a center; deterministic per seed."""
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n
        rr = 1 + rnd.uniform(-wobble, wobble)
        pts.append((cx + math.cos(a)*rx*rr, cy + math.sin(a)*ry*rr))
    catmull(ctx, pts, closed=True)

def fill(ctx, color, a=1.0):
    r,g,b = color; ctx.set_source_rgba(r,g,b,a); ctx.fill()

def mottle(ctx, cx, cy, rx, ry, color, seed, count=26, a=0.10, scale=0.42):
    """Organic large-scale shading: overlapping soft translucent blobs inside
    the current-clip region. Reads as natural ground variation, not confetti."""
    rnd = random.Random(seed)
    r,g,b = color
    for _ in range(count):
        x = cx + rnd.uniform(-rx, rx); y = cy + rnd.uniform(-ry, ry)
        rad = rnd.uniform(rx*scale*0.4, rx*scale)
        rg = cairo.RadialGradient(x,y,0, x,y,rad)
        rg.add_color_stop_rgba(0, r,g,b,a)
        rg.add_color_stop_rgba(1, r,g,b,0)
        ctx.set_source(rg); ctx.arc(x,y,rad,0,2*math.pi); ctx.fill()

def soft_shadow(ctx, cx, cy, r, a=0.28):
    rg = cairo.RadialGradient(cx,cy,r*0.3, cx,cy,r)
    rg.add_color_stop_rgba(0,0,0,0,a); rg.add_color_stop_rgba(1,0,0,0,0)
    ctx.set_source(rg); ctx.arc(cx,cy,r,0,2*math.pi); ctx.fill()

def title(ctx, text, x, y, size=26):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ctx.set_source_rgba(0,0,0,0.55)
    ctx.move_to(x+2,y+2); ctx.show_text(text)
    ctx.set_source_rgb(0.96,0.96,0.94)
    ctx.move_to(x,y); ctx.show_text(text)

def label(ctx, text, x, y, size=13, dot=True):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ext = ctx.text_extents(text)
    pad = 5
    bx, by = x, y - ext.height
    ctx.set_source_rgba(0.05,0.05,0.06,0.72)
    ctx.rectangle(bx-pad, by-pad, ext.width+2*pad, ext.height+2*pad)
    ctx.fill()
    ctx.set_source_rgb(0.97,0.95,0.86)
    ctx.move_to(x, y); ctx.show_text(text)

# ================================================================== BASE MAP
def draw_base(ctx):
    # ground: uniform sand
    ctx.rectangle(0,0,W,H); fill(ctx, rgb("sand"))
    ctx.save(); ctx.rectangle(0,0,W,H); ctx.clip()
    mottle(ctx, W/2,H/2, W/2,H/2, rgb("sand_lo"), 1, count=20, a=0.06)
    ctx.restore()

    # ocean: straight flat band, hard edge, single shade
    ctx.rectangle(0,0,160,H); fill(ctx, rgb("shallow"))
    ctx.rectangle(0,0,70,H);  fill(ctx, rgb("deep"))

    # rock massif: plain blob, one tone, no interior
    ctx.save()
    blobpath(ctx, 650, 250, 150, 210, seed=7, wobble=0.16); ctx.clip()
    ctx.rectangle(460,0,300,540); fill(ctx, rgb("rock"))
    mottle(ctx, 650,250, 150,210, rgb("rock_lo"), 8, count=16, a=0.10)
    ctx.restore()

    # gravel patch: plain
    ctx.save(); blobpath(ctx, 520, 640, 95, 60, seed=9, wobble=0.14); ctx.clip()
    ctx.rectangle(410,560,230,200); fill(ctx, rgb("gravel"))
    ctx.restore()

    title(ctx, "BEFORE  ·  raw player map", 20, 40)

# ============================================================== IMPROVED MAP
def draw_improved(ctx):
    # ---- base sand ground with organic shading -------------------------
    ctx.rectangle(0,0,W,H); fill(ctx, rgb("sand"))
    ctx.save(); ctx.rectangle(0,0,W,H); ctx.clip()
    mottle(ctx, 380,380, 380,380, rgb("sand_hi"), 21, count=16, a=0.05)
    mottle(ctx, 380,380, 380,380, rgb("sand_lo"), 22, count=18, a=0.05)
    ctx.restore()

    # ================================================================= OCEAN
    # Coastline centerline: meanders — headland bulge (top), deep cove (mid),
    # gentle point (bottom). I choose every vertex.
    coast = [(150,-10),(168,70),(205,180),(212,255),   # headland out
             (170,360),(120,455),(112,500),            # cove cut-in
             (150,600),(178,690),(165,780)]
    # water body = left edge + coast
    ctx.save()
    ctx.move_to(0,-10)
    for x,y in coast: ctx.line_to(x,y)
    ctx.line_to(0,780); ctx.close_path(); ctx.clip()
    # depth gradient W->E: deep -> shallow
    g = cairo.LinearGradient(0,0,215,0)
    g.add_color_stop_rgb(0.00, *rgb("deep"))
    g.add_color_stop_rgb(0.55, *rgb("deep"))
    g.add_color_stop_rgb(0.80, *rgb("shallow"))
    g.add_color_stop_rgb(1.00, 0.30,0.52,0.56)  # near-shore lightening
    ctx.set_source(g); ctx.paint()
    # subtle water motion
    mottle(ctx, 90,380, 110,400, rgb("deep"), 31, count=14, a=0.08, scale=0.6)
    ctx.restore()

    # beach: wet-sand strip just inland of the coast (follows the curve)
    ctx.save()
    ctx.move_to(*coast[0])
    catmull(ctx, coast, closed=False)
    # walk back offset inland to make a ribbon
    for x,y in reversed([(cx+60, cy) for cx,cy in coast]):
        ctx.line_to(x,y)
    ctx.close_path(); ctx.clip()
    # wet->dry gradient across the beach ribbon (darker damp sand at waterline)
    g = cairo.LinearGradient(120,0,270,0)
    g.add_color_stop_rgb(0.0, 0.62,0.57,0.44)   # damp
    g.add_color_stop_rgb(1.0, *rgb("beach"))      # drying to dry beach
    ctx.set_source(g); ctx.paint()
    mottle(ctx, 170,380,90,400, rgb("sand"), 41, count=16, a=0.10, scale=0.5)
    ctx.restore()

    # offshore sandbar islet in the cove shallows
    ctx.save(); blobpath(ctx, 92, 430, 26, 12, seed=44, wobble=0.3); ctx.clip()
    fill(ctx, rgb("beach"));
    ctx.restore()
    ctx.save(); blobpath(ctx, 92, 430, 17, 7, seed=45, wobble=0.3); ctx.clip()
    fill(ctx, rgb("sand")); ctx.restore()

    # ============================================================ ROCK MASSIF
    ctx.save()
    blobpath(ctx, 655, 250, 150, 215, seed=7, wobble=0.17); ctx.clip()
    # base rock + light/shadow modelling (NW light)
    ctx.rectangle(460,0,300,540); fill(ctx, rgb("rock"))
    g = cairo.LinearGradient(520,60,760,470)
    g.add_color_stop_rgba(0, *rgb("rock_hi"), 0.55)
    g.add_color_stop_rgba(1, *rgb("rock_lo"), 0.6)
    ctx.set_source(g); ctx.paint()
    mottle(ctx, 655,250,150,215, rgb("rock_lo"), 71, count=20, a=0.12)
    mottle(ctx, 655,250,150,215, rgb("rock_hi"), 72, count=14, a=0.08)
    ctx.restore()
    # massif outline crisp
    ctx.save(); blobpath(ctx,655,250,150,215,seed=7,wobble=0.17)
    ctx.set_source_rgba(*rgb("rock_lo"),0.7); ctx.set_line_width(3); ctx.stroke()
    ctx.restore()

    # talus / scree apron at the massif's west foot
    ctx.save(); blobpath(ctx, 545, 330, 70, 95, seed=73, wobble=0.35); ctx.clip()
    fill(ctx, rgb("scree"), 0.85)
    mottle(ctx, 545,330,70,95, rgb("gravel"), 74, count=24, a=0.14, scale=0.3)
    ctx.restore()

    # ------ CAVERN: chamber carved into SE of massif, mouth toward the flat
    ctx.save(); blobpath(ctx, 662, 372, 52, 46, seed=75, wobble=0.28); ctx.clip()
    fill(ctx, rgb("cave"))
    soft_shadow(ctx, 662,372, 55, a=0.5)
    ctx.restore()
    # cave mouth (a throat opening SW toward the sand)
    ctx.save()
    ctx.move_to(628,352); ctx.curve_to(600,370,600,398,630,410)
    ctx.curve_to(645,398,648,372,628,352); ctx.close_path(); ctx.clip()
    fill(ctx, rgb("cave"))
    ctx.restore()
    label(ctx, "cavern", 636, 380)

    # ---- ABANDONED MINE on the massif's west flank + tailings fan ----
    mx,my = 578, 205
    # tailings: gravel fan spilling downslope (SW)
    ctx.save(); blobpath(ctx, mx-24, my+42, 40, 26, seed=81, wobble=0.3); ctx.clip()
    fill(ctx, rgb("gravel"),0.9)
    mottle(ctx, mx-24,my+42,40,26, rgb("scree"),82,count=16,a=0.14,scale=0.3)
    ctx.restore()
    # adit: dark opening + timber frame
    ctx.save()
    ctx.arc(mx,my,15,0,2*math.pi); ctx.clip(); fill(ctx, rgb("cave"))
    ctx.restore()
    ctx.set_line_width(4); ctx.set_source_rgb(0.32,0.24,0.15)  # timber
    ctx.move_to(mx-14,my+10); ctx.line_to(mx-14,my-12)
    ctx.line_to(mx+14,my-12); ctx.line_to(mx+14,my+10); ctx.stroke()
    ctx.move_to(mx-17,my-12); ctx.line_to(mx+17,my-12); ctx.stroke()
    label(ctx, "abandoned mine", mx-30, my-24)

    # ============================================================ SAND FLAT
    # ---- DRY WASH (arroyo): meanders SW -> NE across the flat -----------
    wash = [(210,690),(258,612),(300,548),(348,470),
            (402,430),(452,392),(506,320),(552,250),(590,196)]
    # soil banks (wider, soft) under the gravel channel
    ctx.save()
    catmull(ctx, wash, closed=False)
    ctx.set_line_width(30); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgba(*rgb("soil"),0.5); ctx.stroke()
    ctx.restore()
    # gravel channel
    ctx.save()
    catmull(ctx, wash, closed=False)
    ctx.set_line_width(15); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(*rgb("gravel")); ctx.stroke()
    ctx.restore()
    # dry braided center
    ctx.save()
    catmull(ctx, wash, closed=False)
    ctx.set_line_width(5); ctx.set_source_rgba(*rgb("scree"),0.8); ctx.stroke()
    ctx.restore()

    # ---- FERTILE HOLLOW at a wash bend (the farm start) ----------------
    ctx.save(); blobpath(ctx, 402, 432, 58, 44, seed=51, wobble=0.24); ctx.clip()
    fill(ctx, rgb("soil"))
    mottle(ctx, 402,432,58,44, rgb("soil_rich"), 52, count=18, a=0.18, scale=0.4)
    ctx.restore()
    ctx.save(); blobpath(ctx, 402,432, 36,26, seed=53, wobble=0.3); ctx.clip()
    fill(ctx, rgb("soil_rich"),0.9)
    # green flush of growth over the richest soil
    mottle(ctx, 402,432,36,26, rgb("fertile"), 57, count=16, a=0.22, scale=0.45)
    ctx.restore()
    label(ctx, "fertile hollow", 356, 476)

    # ---- SCRUB STANDS: coherent green clumps, near the wash ------------
    # each stand = a cluster of little bushes (dark base + lit top), not a wash
    for sx,sy,sr,sd in [(300,560,22,61),(345,505,17,62),(468,360,19,63),
                        (250,640,16,64),(432,470,14,65),(360,590,15,66)]:
        rnd = random.Random(sd)
        nb = max(4, int(sr/3))
        for _ in range(nb):
            bx = sx + rnd.uniform(-sr, sr); by = sy + rnd.uniform(-sr*0.8, sr*0.8)
            br = rnd.uniform(3.2, 6.0)
            ctx.arc(bx, by+1.5, br, 0, 2*math.pi)
            ctx.set_source_rgba(*rgb("scrub"), 0.9); ctx.fill()          # bush body
            ctx.arc(bx-br*0.3, by-br*0.3, br*0.6, 0, 2*math.pi)
            ctx.set_source_rgba(*rgb("scrub_hi"), 0.85); ctx.fill()      # lit crown

    # ---- OUTCROP KNOLL: small rock high-ground mid-flat ----------------
    ctx.save(); blobpath(ctx, 322, 330, 40, 32, seed=54, wobble=0.28); ctx.clip()
    fill(ctx, rgb("scree"))
    mottle(ctx, 322,330,40,32, rgb("gravel"), 55, count=14, a=0.12, scale=0.35)
    ctx.restore()
    ctx.save(); blobpath(ctx, 322, 326, 22, 17, seed=56, wobble=0.26); ctx.clip()
    fill(ctx, rgb("rock"));
    g=cairo.LinearGradient(300,310,344,344)
    g.add_color_stop_rgba(0,*rgb("rock_hi"),0.5); g.add_color_stop_rgba(1,*rgb("rock_lo"),0.5)
    ctx.set_source(g); ctx.paint(); ctx.restore()
    label(ctx, "outcrop knoll", 288, 300)

    # ============================================= CRASHED FACTORY-SHIP SCAR
    # A long scorched furrow gouged NW->SE across the north flat, with a
    # broken hull fragment at the terminus and a debris scatter.
    scar = [(292,64),(352,104),(424,146),(470,180)]
    # broad scorched halo (soft, irregular) — the burn spread, not a stripe
    for sx,sy,sd in [(300,74,131),(340,96,132),(380,120,133),(420,142,134),
                     (455,166,135)]:
        ctx.save(); blobpath(ctx, sx,sy, 40,30, seed=sd, wobble=0.4); ctx.clip()
        fill(ctx, rgb("scorch"), 0.16); ctx.restore()
    # the gouge itself: a tapering furrow, darker toward the impact end
    ctx.save()
    catmull(ctx, scar, closed=False)
    ctx.set_line_width(30); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    g = cairo.LinearGradient(292,64,470,180)
    g.add_color_stop_rgba(0, *rgb("sand_lo"), 0.5)   # shallow start
    g.add_color_stop_rgba(1, *rgb("scorch"), 0.72)   # deep charred end
    ctx.set_source(g); ctx.stroke()
    ctx.restore()
    # churned-earth center line + torn plough ridges either side
    ctx.save()
    catmull(ctx, scar, closed=False)
    ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(*rgb("scorch"),0.85); ctx.stroke()
    ctx.restore()
    # hull fragment (angular metal wreck) at the furrow's end
    ctx.save()
    ctx.translate(478,188); ctx.rotate(0.5)
    ctx.move_to(-46,-26); ctx.line_to(40,-34); ctx.line_to(52,20)
    ctx.line_to(-30,34); ctx.close_path()
    ctx.set_source_rgb(*rgb("metal")); ctx.fill_preserve()
    ctx.set_source_rgba(*rgb("ink"),0.6); ctx.set_line_width(2); ctx.stroke()
    # hull panel highlights + a torn rib
    ctx.move_to(-40,-18); ctx.line_to(34,-26)
    ctx.set_source_rgba(*rgb("metal_hi"),0.8); ctx.set_line_width(3); ctx.stroke()
    ctx.move_to(-10,-30); ctx.line_to(-6,28)
    ctx.set_source_rgba(*rgb("ink"),0.5); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    # scattered debris chunks
    for dx,dy,dr,dd in [(360,120,7,91),(400,95,5,92),(330,150,6,93),
                        (445,215,6,94),(505,168,5,95),(300,105,4,96)]:
        ctx.save(); blobpath(ctx, dx,dy,dr,dr*0.8,seed=dd,wobble=0.3); ctx.clip()
        fill(ctx, rgb("metal"),0.9); ctx.restore()
    label(ctx, "crashed Factory-ship", 300, 60)

    # ================================ DEAD DROID IN IMPACT CRATER (S flat)
    cx,cy = 250, 545
    # crater: raised rim ring + dark bowl
    ctx.save(); blobpath(ctx, cx,cy, 46,40, seed=101, wobble=0.16); ctx.clip()
    fill(ctx, rgb("sand_lo"))
    ctx.restore()
    ctx.save(); blobpath(ctx, cx,cy, 34,29, seed=102, wobble=0.16); ctx.clip()
    fill(ctx, rgb("scorch"),0.35)
    soft_shadow(ctx, cx,cy, 34, a=0.35)
    ctx.restore()
    # scorch streak
    ctx.save(); blobpath(ctx, cx-6,cy+4, 22,18, seed=103, wobble=0.3); ctx.clip()
    fill(ctx, rgb("scorch"),0.5); ctx.restore()
    # toppled droid: body + limb + dead optic
    ctx.save(); ctx.translate(cx+4,cy+2); ctx.rotate(-0.6)
    ctx.rectangle(-13,-8,26,16)
    ctx.set_source_rgb(*rgb("metal")); ctx.fill_preserve()
    ctx.set_source_rgba(*rgb("ink"),0.6); ctx.set_line_width(1.5); ctx.stroke()
    ctx.rectangle(11,-3,10,6); ctx.set_source_rgb(*rgb("metal_hi")); ctx.fill()  # head
    ctx.arc(16,0,2.0,0,2*math.pi); ctx.set_source_rgb(0.7,0.15,0.12); ctx.fill() # dead optic
    ctx.move_to(-10,8); ctx.line_to(-20,20)  # splayed limb
    ctx.set_source_rgb(*rgb("metal")); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()
    label(ctx, "dead droid · impact crater", cx-40, cy+64)

    # ============================ GRAVEL FLAT (SE) + SEMI-WORKING REFINERY
    ctx.save(); blobpath(ctx, 520, 648, 110, 68, seed=9, wobble=0.16); ctx.clip()
    fill(ctx, rgb("gravel"))
    mottle(ctx, 520,648,110,68, rgb("scree"), 111, count=20, a=0.10, scale=0.35)
    ctx.restore()

    # refinery: ancient-concrete pad + tanks + pipes + a ruptured tank stain
    ctx.save()
    ctx.rectangle(452,596,150,104)
    ctx.set_source_rgba(*rgb("concrete"),0.95); ctx.fill_preserve()
    ctx.set_source_rgba(*rgb("ink"),0.35); ctx.set_line_width(2); ctx.stroke()
    ctx.restore()
    # cracks on the pad
    ctx.set_source_rgba(*rgb("ink"),0.3); ctx.set_line_width(1.2)
    ctx.move_to(470,610); ctx.line_to(520,660); ctx.line_to(560,640); ctx.stroke()
    # spill stain from ruptured tank
    ctx.save(); blobpath(ctx, 560,672, 34,20, seed=121, wobble=0.4); ctx.clip()
    fill(ctx, rgb("scorch"),0.4); ctx.restore()
    # tank 1 (intact)
    def tank(tx,ty,r,intact=True):
        rg=cairo.RadialGradient(tx-r*0.35,ty-r*0.35,r*0.1, tx,ty,r)
        rg.add_color_stop_rgb(0,*rgb("metal_hi")); rg.add_color_stop_rgb(1,*rgb("metal"))
        ctx.set_source(rg); ctx.arc(tx,ty,r,0,2*math.pi); ctx.fill()
        ctx.set_source_rgba(*rgb("ink"),0.5); ctx.set_line_width(2)
        ctx.arc(tx,ty,r,0,2*math.pi); ctx.stroke()
        if not intact:  # ruptured: dark gash + rust
            ctx.save(); ctx.arc(tx,ty,r,0,2*math.pi); ctx.clip()
            ctx.set_source_rgba(*rgb("rust"),0.7)
            ctx.move_to(tx-2,ty-r); ctx.line_to(tx+8,ty); ctx.line_to(tx-4,ty+r)
            ctx.line_to(tx-14,ty); ctx.close_path(); ctx.fill(); ctx.restore()
    tank(486,626,18,True)
    tank(486,672,15,True)
    tank(556,632,20,False)  # ruptured
    # pipes connecting tanks
    ctx.set_source_rgb(*rgb("metal")); ctx.set_line_width(4)
    ctx.move_to(504,626); ctx.line_to(536,632); ctx.stroke()
    ctx.move_to(486,644); ctx.line_to(486,657); ctx.stroke()
    # a small derrick (triangle mast)
    ctx.set_source_rgba(*rgb("metal_hi"),0.9); ctx.set_line_width(2.5)
    ctx.move_to(590,700); ctx.line_to(578,650); ctx.line_to(600,650); ctx.close_path(); ctx.stroke()
    label(ctx, "semi-working refinery", 452, 588)

    title(ctx, "AFTER  ·  LLM-authored improvements", 20, 40)

# ------------------------------------------------------------------ compose
def render_panel(which, path):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    (draw_base if which=="base" else draw_improved)(c)
    # thin frame
    c.set_source_rgba(0,0,0,0.5); c.set_line_width(3)
    c.rectangle(1.5,1.5,W-3,H-3); c.stroke()
    s.write_to_png(path)

def render_pair(path):
    gap = 20
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W*2+gap, H)
    c = cairo.Context(s)
    c.set_source_rgb(1,1,1); c.paint()
    for i,which in enumerate(("base","improved")):
        sub = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        cc = cairo.Context(sub)
        (draw_base if which=="base" else draw_improved)(cc)
        cc.set_source_rgba(0,0,0,0.5); cc.set_line_width(3)
        cc.rectangle(1.5,1.5,W-3,H-3); cc.stroke()
        c.set_source_surface(sub, i*(W+gap), 0); c.paint()
    s.write_to_png(path)

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv)>1 else "."
    render_panel("base", f"{out}/coastal_mesa_before.png")
    render_panel("improved", f"{out}/coastal_mesa_after.png")
    render_pair(f"{out}/coastal_mesa_pair.png")
    print("wrote before / after / pair to", out)
