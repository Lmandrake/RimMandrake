#!/usr/bin/env python3
"""Procedural suspension-bridge parts in four looks. Usage: gen.py <outroot>  (writes <outroot>/<Look>/RM_*.png)."""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 256
LOOKS = ['Scrapper', 'Industrial', 'Modern', 'Futuristic']
P = {
 'Scrapper':   dict(wood=[(124,90,58),(100,72,46),(142,106,70),(86,66,48),(112,84,60)], dark=(52,40,30), metal=(150,88,54), tin=(122,128,130), rope=(184,156,104), accent=(198,160,60), glow=None),
 'Industrial': dict(wood=[(78,60,46),(70,54,42)], steel=(96,102,108), dark=(48,52,56), hz=(220,172,26), black=(28,28,30), rivet=(158,164,170), glow=None),
 'Modern':     dict(conc=(172,172,166), wood=[(200,152,98),(190,144,90)], red=(196,38,34), zinc=(176,182,188), dark=(62,62,66), glow=None),
 'Futuristic': dict(white=(234,238,242), grey=(188,198,208), dark=(52,62,74), cyan=(70,222,255), glow=(70,222,255)),
}

class PD(dict):
    def __missing__(self, k): return (128, 128, 128)
P = {k: PD(v) for k, v in P.items()}

def mul(c, f): return tuple(max(0, min(255, int(v*f))) for v in c)

def noise(h, w, scale, seed):
    r = np.random.RandomState(seed)
    a = r.rand(max(2, h//scale+2), max(2, w//scale+2)).astype(np.float32)
    im = Image.fromarray((a*255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32)/255.0

def tex(w, h, base, var=0.12, grain=None, seed=0, fine=0.05):
    n = noise(h, w, 24, seed) - 0.5
    f = 1 + n*var*2
    if grain == 'v':
        g = noise(h, w, 4, seed+7)  # placeholder, replaced below
        g = np.tile(noise(1, w, 2, seed+3), (h, 1)) - 0.5
        f = f + g*0.22
    elif grain == 'h':
        g = np.tile(noise(h, 1, 2, seed+3), (1, w)) - 0.5
        f = f + g*0.22
    f = f + (np.random.RandomState(seed+9).rand(h, w)-0.5)*fine*2
    out = np.clip(np.array(base, np.float32)[None, None, :]*f[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(out, 'RGB')

def paste(img, t, x0, y0, mask=None):
    if mask is None: img.paste(t.convert('RGBA'), (x0, y0))
    else: img.paste(t.convert('RGBA'), (x0, y0), mask)

def box_tex(img, box, base, **kw):
    x0, y0, x1, y1 = box
    paste(img, tex(x1-x0, y1-y0, base, **kw), x0, y0)

def shade(img, box, axis='h', hi=1.18, lo=0.78):
    """multiply a gradient over a box (axis h: across width, v: down height); alpha untouched."""
    x0, y0, x1, y1 = box
    w, h = x1-x0, y1-y0
    a = np.asarray(img.crop(box)).astype(np.float32)
    t = np.linspace(hi, lo, w if axis == 'h' else h, dtype=np.float32)
    g = t[None, :, None] if axis == 'h' else t[:, None, None]
    a[..., :3] = np.clip(a[..., :3]*g, 0, 255)
    img.paste(Image.fromarray(a.astype(np.uint8), 'RGBA'), (x0, y0))

def outline(d, box, col=(20, 18, 16, 255), r=0):
    d.rectangle(box, outline=col)

def rivet(d, x, y, col, r=3):
    d.ellipse((x-r, y-r, x+r, y+r), fill=mul(col, 0.7)+(255,))
    d.ellipse((x-r+1, y-r+1, x+r-1, y+r-1), fill=col+(255,))
    d.point((x-1, y-1), fill=mul(col, 1.4)+(255,))

def bar(img, box, col, axis='v', hi=1.3, lo=0.7, grain=None, seed=0, edge=True):
    """a shaded bar; axis = direction the shading runs across."""
    x0, y0, x1, y1 = box
    paste(img, tex(x1-x0, y1-y0, col, var=0.08, grain=grain, seed=seed), x0, y0)
    shade(img, box, 'v' if axis == 'v' else 'h', hi, lo)
    if edge: ImageDraw.Draw(img).rectangle((x0, y0, x1-1, y1-1), outline=mul(col, 0.35)+(255,))

def hazard(img, box, y_col, b_col, pitch=18, diag=True, seed=0):
    x0, y0, x1, y1 = box
    w, h = x1-x0, y1-y0
    yy, xx = np.mgrid[0:h, 0:w]
    m = (((xx + yy) // (pitch//2)) % 2 == 0)
    a = np.zeros((h, w, 3), np.uint8); a[m] = y_col; a[~m] = b_col
    t = Image.fromarray(a, 'RGB')
    t = Image.blend(t, tex(w, h, (200, 200, 200), var=.2, seed=seed), 0.12)
    paste(img, t, x0, y0)

def new(): return Image.new('RGBA', (S, S), (0, 0, 0, 0))

def finish(img, sat_noise=True):
    a = np.asarray(img).copy()
    return Image.fromarray(a, 'RGBA')

# ---------------------------------------------------------------- deck
BAND = 28

def side_band(img, look, x0, x1, seed):
    p = P[look]; d = ImageDraw.Draw(img)
    box = (x0, 0, x1, S)
    if look == 'Scrapper':
        # mismatched logs / pipe lengths lashed with rope
        y = 0; i = 0
        while y < S:
            L = random.Random(seed+i).randint(46, 96); y1 = min(S, y+L)
            col = random.Random(seed+i).choice([(96, 70, 46), (82, 62, 44), p['metal'], (112, 82, 54)])
            bar(img, (x0, y, x1, y1), col, 'h', hi=1.25, lo=0.72, grain='h' if col[0] < 130 else None, seed=seed+i)
            y = y1; i += 1
        for yy in range(20, S, 64):
            d.rectangle((x0, yy, x1-1, yy+5), fill=p['rope']+(255,))
            for k in range(x0, x1, 4): d.line((k, yy, k+3, yy+5), fill=mul(p['rope'], .6)+(255,))
    elif look == 'Industrial':
        box_tex(img, box, p['steel'], var=.1, grain='v', seed=seed)
        shade(img, box, 'h', 1.15, .8)
        inner = x1-10 if x0 == 0 else x0
        hazard(img, (inner, 0, inner+10, S), p['hz'], p['black'], seed=seed)
        d.rectangle((x0, 0, x1-1, S-1), outline=(22, 24, 26, 255))
        for yy in range(16, S, 48): rivet(d, (x0+9) if x0 == 0 else (x1-9), yy, p['rivet'], 3)
    elif look == 'Modern':
        box_tex(img, box, p['red'], var=.05, grain='v', seed=seed)
        shade(img, box, 'h', 1.22, .78)
        d.rectangle((x0, 0, x1-1, S-1), outline=mul(p['red'], .4)+(255,))
        for yy in range(16, S, 48):
            for xx in ((x0+9, x0+19) if x0 == 0 else (x1-19, x1-9)): rivet(d, xx, yy, p['zinc'], 2)
    else:
        box_tex(img, box, p['grey'], var=.04, seed=seed)
        shade(img, box, 'h', 1.15, .85)
        d.rectangle((x0, 0, x1-1, S-1), outline=p['dark']+(255,))
        cx = x0+8 if x0 == 0 else x1-11
        d.rectangle((cx, 0, cx+2, S), fill=p['cyan']+(255,))
        for yy in range(0, S, 64): d.rectangle((cx-1, yy+30, cx+3, yy+34), fill=(220, 252, 255, 255))

def deck_center(img, look, seed):
    p = P[look]; d = ImageDraw.Draw(img); x0, x1 = BAND, S-BAND
    if look == 'Scrapper':
        x = x0; i = 0
        while x < x1:
            w = random.Random(seed+i).randint(20, 34); w = min(w, x1-x)
            if x1-(x+w) < 12: w = x1-x
            col = random.Random(seed+i*3).choice(p['wood'])
            box_tex(img, (x, 0, x+w, S), col, var=.16, grain='v', seed=seed+i*5, fine=.06)
            shade(img, (x, 0, x+w, S), 'h', 1.12, .88)
            d.line((x, 0, x, S), fill=(30, 22, 16, 255), width=2)
            # splits and nails
            r = random.Random(seed+i)
            for _ in range(3):
                sy = r.randint(0, S-30); d.line((x+w//2+r.randint(-4, 4), sy, x+w//2+r.randint(-3, 3), sy+r.randint(8, 26)), fill=(40, 28, 20, 255))
            i += 1; x += w
        # rusty tin patches
        for (px, py, pw, ph) in [(54, 30, 62, 48), (128, 150, 74, 54)]:
            t = tex(pw, ph, p['metal'], var=.22, seed=seed+px)
            paste(img, t, px, py); d.rectangle((px, py, px+pw-1, py+ph-1), outline=(60, 34, 22, 255))
            for cx, cy in [(px+5, py+5), (px+pw-6, py+5), (px+5, py+ph-6), (px+pw-6, py+ph-6)]: rivet(d, cx, cy, (120, 120, 118), 2)
        # rope lashings across
        for yy in (92, 210):
            d.rectangle((x0, yy, x1-1, yy+7), fill=p['rope']+(255,))
            for k in range(x0, x1, 5): d.line((k, yy, k+4, yy+7), fill=mul(p['rope'], .62)+(255,))
            d.line((x0, yy+7, x1, yy+7), fill=(50, 38, 24, 255))
    elif look == 'Industrial':
        for i, y in enumerate(range(0, S, 64)):
            box_tex(img, (x0, y, x1, y+64), p['steel'] if i % 2 == 0 else mul(p['steel'], .9), var=.09, grain='h', seed=seed+i, fine=.04)
            shade(img, (x0, y, x1, y+64), 'v', 1.1, .9)
            d.rectangle((x0, y, x1-1, y+63), outline=(26, 28, 30, 255))
            for xx in list(range(x0+10, x1-8, 30)): rivet(d, xx, y+8, p['rivet'], 3); rivet(d, xx, y+56, p['rivet'], 3)
            # checker-plate diamonds
            for xx in range(x0+14, x1-14, 18):
                for yy in range(y+20, y+46, 12):
                    d.line((xx-4, yy+2, xx+4, yy-2), fill=mul(p['steel'], 1.4)+(255,), width=2)
    elif look == 'Modern':
        for i, y in enumerate(range(0, S, 86)):
            y1 = min(S, y+86)
            box_tex(img, (x0, y, x1, y1), p['conc'], var=.07, seed=seed+i, fine=.07)
            d.rectangle((x0, y, x1-1, y1-1), outline=mul(p['conc'], .55)+(255,))
            d.line((x0, y1-1, x1, y1-1), fill=mul(p['conc'], .45)+(255,), width=2)
            for xx in (x0+8, x1-9):
                for yy in (y+8, y1-9): d.ellipse((xx-2, yy-2, xx+2, yy+2), fill=mul(p['conc'], .6)+(255,))
        # painted lane line
        d.rectangle((126, 0, 129, S), fill=(238, 214, 90, 255))
        for yy in range(0, S, 40): d.rectangle((126, yy+28, 129, yy+39), fill=mul(p['conc'], 1.0)+(255,))
    else:
        for i, y in enumerate(range(0, S, 64)):
            box_tex(img, (x0, y, x1, y+64), p['white'], var=.03, seed=seed+i, fine=.03)
            shade(img, (x0, y, x1, y+64), 'v', 1.04, .94)
            d.rectangle((x0, y, x1-1, y+63), outline=mul(p['grey'], .85)+(255,))
            d.rectangle((x0+6, y+6, x1-7, y+57), outline=mul(p['grey'], .95)+(255,))
            d.rectangle((x0+10, y+30, x1-11, y+33), fill=p['cyan']+(255,))
            for xx in (x0+14, x1-15): d.ellipse((xx-2, y+10, xx+2, y+14), fill=p['grey']+(255,))
        d.rectangle((126, 0, 129, S), fill=mul(p['cyan'], 1.0)+(255,))

def deck(look):
    img = new(); deck_center(img, look, 11)
    side_band(img, look, 0, BAND, 31); side_band(img, look, S-BAND, S, 71)
    return img

def grated(look):
    p = P[look]; img = new(); d = ImageDraw.Draw(img)
    r = random.Random(5)
    col = {'Scrapper': (116, 88, 60), 'Industrial': p['steel'], 'Modern': p['zinc'], 'Futuristic': p['white']}[look]
    x0, x1 = BAND, S-BAND
    # longitudinal stringers
    for xx in (82, 170):
        bar(img, (xx, 0, xx+7, S), mul(col, .9), 'h', hi=1.3, lo=.7, seed=xx)
    # cross bars
    for i, y in enumerate(range(6, S, 20)):
        off = r.randint(-2, 2) if look == 'Scrapper' else 0
        th = 8 if look != 'Scrapper' else r.choice([7, 8, 9])
        c = col if look != 'Scrapper' else r.choice([col, p['wood'][0], p['wood'][3], p['metal']])
        bar(img, (x0, y+off, x1, y+off+th), c, 'v', hi=1.3, lo=.68, grain='h' if look == 'Scrapper' else None, seed=i)
        if look == 'Futuristic': d.line((x0, y+3, x1, y+3), fill=p['cyan']+(255,))
    if look == 'Scrapper':
        for yy in (66, 186):
            for xx in (82, 170): d.rectangle((xx-1, yy, xx+8, yy+5), fill=p['rope']+(255,))
    if look == 'Industrial':
        for i, y in enumerate(range(6, S, 20)):
            for xx in (85, 173): rivet(d, xx, y+4, p['rivet'], 2)
    side_band(img, look, 0, BAND, 31); side_band(img, look, S-BAND, S, 71)
    return img

# ---------------------------------------------------------------- rail edge
def rail(look):
    p = P[look]; img = new(); d = ImageDraw.Draw(img)
    def hbar(y0, y1, col, hi=1.35, lo=.65): bar(img, (0, y0, S, y1), col, 'v', hi, lo, seed=y0)
    posts = list(range(10, S, 40))
    if look == 'Scrapper':
        hbar(14, 18, (100, 74, 50)); 
        for k in range(0, S, 4): d.point((k, 24+int(2*math.sin(k/9))), fill=p['rope']+(255,)); d.point((k, 25+int(2*math.sin(k/9))), fill=mul(p['rope'], .7)+(255,))
        for i, x in enumerate(posts):
            h = random.Random(i).randint(22, 27)
            bar(img, (x-3, 28-h, x+4, 29), random.Random(i).choice(p['wood']), 'h', 1.25, .7, grain='v', seed=i)
            d.rectangle((x-4, 12, x+5, 16), fill=p['rope']+(255,))
        hbar(5, 10, (120, 90, 60))
    elif look == 'Industrial':
        hbar(4, 11, p['hz']); 
        for k in range(0, S, 24): d.rectangle((k, 4, k+9, 10), fill=p['black']+(255,))
        hbar(17, 21, p['steel'])
        for x in posts: bar(img, (x-3, 2, x+4, 28), p['dark'], 'h', 1.4, .7, seed=x); rivet(d, x, 25, p['rivet'], 2)
    elif look == 'Modern':
        hbar(4, 11, p['red'])
        for yy in (15, 21): d.line((0, yy, S, yy), fill=mul(p['zinc'], .8)+(255,), width=1)
        for x in posts: bar(img, (x-3, 2, x+4, 28), p['zinc'], 'h', 1.4, .65, seed=x)
    else:
        hbar(3, 9, p['white']); d.line((0, 6, S, 6), fill=p['cyan']+(255,), width=2)
        d.line((0, 16, S, 16), fill=p['cyan']+(160,), width=1)
        for x in posts:
            bar(img, (x-3, 2, x+4, 28), p['grey'], 'h', 1.35, .7, seed=x); d.rectangle((x-1, 12, x+1, 14), fill=(220, 252, 255, 255))
    # transparent below the top quarter
    a = np.asarray(img).copy(); a[S//4:, :, 3] = 0
    return Image.fromarray(a, 'RGBA')

# ---------------------------------------------------------------- anchor
def post_asm(look, cx, img):
    p = P[look]; d = ImageDraw.Draw(img)
    x0, x1 = cx-26, cx+26
    # cable
    ccol = {'Scrapper': (150, 120, 76), 'Industrial': (70, 74, 80), 'Modern': (150, 156, 162), 'Futuristic': (60, 70, 82)}[look]
    w = 7 if look != 'Scrapper' else 8
    bar(img, (cx-w//2, 0, cx+w//2+1, 150), ccol, 'h', 1.4, .6, seed=cx)
    for y in range(4, 150, 7): d.line((cx-w//2, y, cx+w//2, y+3), fill=mul(ccol, .55)+(255,))
    if look == 'Futuristic': d.line((cx, 0, cx, 150), fill=p['cyan']+(255,))
    # base plate
    basecol = {'Scrapper': (112, 84, 56), 'Industrial': p['steel'], 'Modern': p['conc'], 'Futuristic': p['white']}[look]
    bar(img, (x0, 212, x1, 240), mul(basecol, .88), 'v', 1.2, .72, seed=cx+1)
    # pylon body
    bodycol = {'Scrapper': (124, 90, 58), 'Industrial': p['dark'], 'Modern': p['red'], 'Futuristic': p['grey']}[look]
    bar(img, (cx-17, 150, cx+18, 214), bodycol, 'h', 1.3, .68, grain='v' if look == 'Scrapper' else None, seed=cx+2)
    # clevis head
    headcol = {'Scrapper': p['metal'], 'Industrial': p['steel'], 'Modern': p['zinc'], 'Futuristic': p['white']}[look]
    bar(img, (cx-16, 126, cx+17, 156), headcol, 'h', 1.3, .65, seed=cx+3)
    d.ellipse((cx-5, 134, cx+5, 144), fill=(20, 20, 22, 255)); d.ellipse((cx-3, 136, cx+3, 142), fill=mul(headcol, .6)+(255,))
    # gussets
    d.polygon([(cx-17, 214), (cx-17, 176), (cx-26, 214)], fill=mul(bodycol, .85)+(255,))
    d.polygon([(cx+18, 214), (cx+18, 176), (cx+27, 214)], fill=mul(bodycol, .7)+(255,))
    if look == 'Scrapper':
        d.rectangle((cx-17, 170, cx+17, 178), fill=p['rope']+(255,))
        for k in range(cx-17, cx+17, 4): d.line((k, 170, k+3, 178), fill=mul(p['rope'], .6)+(255,))
    elif look == 'Industrial':
        hazard(img, (cx-17, 192, cx+18, 204), p['hz'], p['black'], pitch=12)
    elif look == 'Modern':
        for y in (160, 200): rivet(d, cx, y, p['zinc'], 3)
    else:
        d.rectangle((cx-17, 184, cx+17, 187), fill=p['cyan']+(255,))
    for xx in (x0+7, x1-7): rivet(d, xx, 226, mul(headcol, 1.0), 3)

def anchor_north(look):
    img = new()
    post_asm(look, 70, img); post_asm(look, 186, img)
    return img

# ---------------------------------------------------------------- tower
def tower(look):
    p = P[look]; img = new(); d = ImageDraw.Draw(img)
    mask = Image.new('L', (S, S), 0); md = ImageDraw.Draw(mask)
    md.rounded_rectangle((62, 100, 194, 222), 10, fill=255)
    body = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    bodycol = {'Scrapper': (122, 92, 62), 'Industrial': p['steel'], 'Modern': p['conc'], 'Futuristic': p['white']}[look]
    body.paste(tex(S, S, bodycol, var=.1, grain='v' if look == 'Scrapper' else None, seed=3, fine=.06).convert('RGBA'), (0, 0))
    bd = ImageDraw.Draw(body)
    if look == 'Scrapper':
        for x in range(62, 195, 22): bd.line((x, 100, x, 222), fill=(36, 26, 18, 255), width=2)
        for y in (118, 176):
            bd.rectangle((62, y, 194, y+9), fill=p['rope']+(255,))
            for k in range(62, 195, 5): bd.line((k, y, k+4, y+9), fill=mul(p['rope'], .6)+(255,))
        bd.rectangle((70, 140, 112, 170), fill=p['metal']+(255,), outline=(60, 34, 22, 255)); bd.rectangle((140, 186, 186, 214), fill=p['tin']+(255,), outline=(50, 52, 54, 255))
    elif look == 'Industrial':
        for y in (100, 140, 180):
            bd.rectangle((62, y, 194, y+40), outline=(24, 26, 28, 255), width=2)
            for x in (72, 128, 184): rivet(bd, x, y+8, p['rivet'], 3); rivet(bd, x, y+32, p['rivet'], 3)
        hazard(body, (62, 150, 194, 166), p['hz'], p['black'], pitch=16)
    elif look == 'Modern':
        for y in range(100, 222, 30): bd.line((62, y, 194, y), fill=mul(p['conc'], .55)+(255,), width=2)
        for y in range(114, 222, 30):
            for x in (74, 182): bd.ellipse((x-2, y-2, x+2, y+2), fill=mul(p['conc'], .6)+(255,))
        bd.rectangle((62, 160, 194, 172), fill=p['red']+(255,))
    else:
        for y in (118, 164, 200): bd.rectangle((62, y, 194, y+4), fill=p['cyan']+(255,))
        for x in (96, 160): bd.line((x, 100, x, 222), fill=mul(p['grey'], .9)+(255,), width=1)
        bd.rectangle((100, 126, 156, 156), outline=p['grey']+(255,))
    # cylindrical shading
    a = np.asarray(body).astype(np.float32)
    g = np.interp(np.arange(S), [62, 90, 140, 194], [1.18, 1.1, .92, .72])[None, :, None]
    a[..., :3] = np.clip(a[..., :3]*g, 0, 255)
    body = Image.fromarray(a.astype(np.uint8), 'RGBA')
    img.paste(body, (0, 0), mask)
    d = ImageDraw.Draw(img)
    md2 = Image.new('L', (S, S), 0); ImageDraw.Draw(md2).rounded_rectangle((62, 100, 194, 222), 10, outline=255, width=2)
    img.paste(Image.new('RGBA', (S, S), (20, 18, 16, 255)), (0, 0), md2)
    # base flare
    basecol = mul(bodycol, .78)
    bar(img, (52, 218, 204, 237), basecol, 'v', 1.15, .7, seed=8)
    # cap
    capcol = {'Scrapper': p['metal'], 'Industrial': p['dark'], 'Modern': p['red'], 'Futuristic': p['white']}[look]
    capm = Image.new('L', (S, S), 0); ImageDraw.Draw(capm).rounded_rectangle((51, 70, 205, 106), 8, fill=255)
    capt = Image.new('RGBA', (S, S)); capt.paste(tex(S, S, mul(capcol, .8), var=.1, seed=4).convert('RGBA'), (0, 0))
    img.paste(capt, (0, 0), capm)
    ImageDraw.Draw(img).rounded_rectangle((51, 70, 205, 106), 8, outline=(20, 18, 16, 255), width=2)
    topm = Image.new('L', (S, S), 0); ImageDraw.Draw(topm).rounded_rectangle((56, 22, 200, 84), 12, fill=255)
    topt = Image.new('RGBA', (S, S)); topt.paste(tex(S, S, capcol, var=.08, seed=5).convert('RGBA'), (0, 0))
    a = np.asarray(topt).astype(np.float32); a[22:84, :, :3] *= np.linspace(1.15, .88, 62)[:, None, None]
    img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA'), (0, 0), topm)
    d = ImageDraw.Draw(img); d.rounded_rectangle((56, 22, 200, 84), 12, outline=(20, 18, 16, 255), width=2)
    # saddles
    sad = {'Scrapper': (84, 66, 50), 'Industrial': p['steel'], 'Modern': p['zinc'], 'Futuristic': p['grey']}[look]
    for cx in (92, 164):
        bar(img, (cx-22, 30, cx+23, 74), mul(sad, .75), 'h', 1.2, .7, seed=cx)
        bar(img, (cx-12, 24, cx+13, 78), sad, 'h', 1.4, .6, seed=cx+1)
        d.line((cx, 24, cx, 78), fill=(20, 20, 22, 255), width=3)
        for yy in (36, 66): rivet(d, cx-17, yy, p['rivet'] if look == 'Industrial' else (150, 150, 150), 2)
    if look == 'Futuristic': d.rounded_rectangle((60, 26, 196, 80), 10, outline=p['cyan']+(255,), width=2)
    if look == 'Scrapper':
        for cx in (92, 164): d.rectangle((cx-22, 52, cx+22, 57), fill=p['rope']+(255,))
    return img

# ---------------------------------------------------------------- wreck
def piece(look, kind, w, h, seed):
    p = P[look]; r = random.Random(seed)
    if look == 'Scrapper':
        col = r.choice(p['wood'] + [p['metal'], p['tin']]) if kind != 'big' else r.choice(p['wood'])
        t = tex(w, h, col, .15, 'h' if col in p['wood'] else None, seed).convert('RGBA')
    elif look == 'Industrial':
        col = r.choice([p['steel'], p['dark'], p['steel'], p['hz'], p['wood'][0]])
        if col == p['hz']:
            t = Image.new('RGBA', (w, h)); hazard(t, (0, 0, w, h), p['hz'], p['black'], pitch=12)
        else: t = tex(w, h, col, .1, 'h', seed).convert('RGBA')
    elif look == 'Modern':
        col = r.choice([p['conc'], p['conc'], p['red'], p['zinc'], p['wood'][0]])
        t = tex(w, h, col, .09, 'h' if col == p['wood'][0] else None, seed, fine=.07).convert('RGBA')
    else:
        col = r.choice([p['white'], p['white'], p['grey'], p['dark'], p['cyan']])
        t = tex(w, h, col, .05, None, seed).convert('RGBA')
    a = np.asarray(t).astype(np.float32); a[..., :3] *= np.linspace(1.18, .72, h)[:, None, None]
    t = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(t); d.rectangle((0, 0, w-1, h-1), outline=(18, 16, 14, 255))
    if look == 'Futuristic' and col != p['cyan']: d.line((2, h//2, w-3, h//2), fill=p['cyan']+(255,))
    if look in ('Industrial', 'Modern') and w > 30: rivet(d, 6, h//2, (170, 170, 170), 2); rivet(d, w-7, h//2, (170, 170, 170), 2)
    if look == 'Scrapper' and w > 30: d.rectangle((w//3, 0, w//3+3, h), fill=p['rope']+(255,))
    m = Image.new('L', (w, h), 255)
    # ragged broken end
    md = ImageDraw.Draw(m)
    for k in range(0, h, 3): md.line((w-r.randint(0, 6), k, w, k), fill=0)
    return t, m

def wreck(look):
    p = P[look]; r = random.Random(42)
    img = new(); sh = Image.new('L', (S, S), 0); sd = ImageDraw.Draw(sh)
    placed = []
    specs = [('big', 84, 64), ('big', 76, 58)] + [('beam', r.randint(84, 132), r.randint(15, 24)) for _ in range(13)] + [('chunk', r.randint(30, 46), r.randint(24, 36)) for _ in range(8)]
    layers = []
    for i, (kind, w, h) in enumerate(specs):
        t, m = piece(look, kind, w, h, 100+i)
        ang = r.uniform(0, 360)
        rad = r.uniform(0, 64) if kind != 'big' else r.uniform(0, 34)
        th = r.uniform(0, 6.283)
        cx, cy = 128+rad*math.cos(th), 128+rad*math.sin(th)*0.9
        t2 = t.rotate(ang, expand=True, resample=Image.BICUBIC); m2 = m.rotate(ang, expand=True, resample=Image.BICUBIC)
        layers.append((t2, m2, int(cx-t2.width/2), int(cy-t2.height/2)))
    for t2, m2, x, y in layers: sh.paste(255, (x+7, y+9), m2)
    sh = sh.filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v*0.55))
    img.paste(Image.new('RGBA', (S, S), (0, 0, 0, 255)), (0, 0), sh)
    for t2, m2, x, y in layers: img.paste(t2, (x, y), m2)
    d = ImageDraw.Draw(img)
    # dangling cables / frayed wire
    ccol = {'Scrapper': p['rope'], 'Industrial': (60, 64, 70), 'Modern': (130, 136, 142), 'Futuristic': (70, 80, 92)}[look]
    for k in range(4):
        x, y = 128+r.randint(-50, 50), 128+r.randint(-50, 50); pts = [(x, y)]
        a0 = r.uniform(0, 6.28)
        for j in range(8): a0 += r.uniform(-.7, .7); x += 9*math.cos(a0); y += 9*math.sin(a0); pts.append((x, y))
        d.line(pts, fill=(20, 18, 16, 255), width=5); d.line(pts, fill=ccol+(255,), width=3)
        if look == 'Futuristic': d.line(pts, fill=p['cyan']+(255,), width=1)
    # scattered fragments
    for k in range(90):
        th = r.uniform(0, 6.283); rad = r.uniform(40, 112)
        x, y = 128+rad*math.cos(th), 128+rad*math.sin(th)*.9
        if look == 'Scrapper': col = r.choice(p['wood'] + [p['metal'], p['rope']])
        elif look == 'Industrial': col = r.choice([p['steel'], p['dark'], p['hz'], (110, 64, 40)])
        elif look == 'Modern': col = r.choice([p['conc'], p['red'], p['zinc']])
        else: col = r.choice([p['white'], p['grey'], p['cyan']])
        s = r.randint(2, 5)
        d.polygon([(x, y), (x+s, y+r.randint(0, s)), (x+r.randint(0, s), y+s+1)], fill=col+(255,), outline=(20, 18, 16, 255))
    # keep corners clean
    a = np.asarray(img).copy(); yy, xx = np.mgrid[0:S, 0:S]; a[(np.hypot(xx-127.5, yy-127.5) > 122), 3] = 0
    return Image.fromarray(a, 'RGBA')

# ---------------------------------------------------------------- jetty
def jetty_north(look):
    p = P[look]; img = new(); d = ImageDraw.Draw(img)
    X0, X1, Y0 = 36, 220, 26    # outer extent; root bleeds off the bottom
    R = 12                       # rail thickness
    # platform plates
    dk = deck(look).crop((X0+R-BAND+8, 0, X0+R-BAND+8+(X1-X0-2*R), S))  # reuse deck texture (runs N-S)
    pw = X1-X0-2*R
    pt = deck(look)
    mid = pt.crop((BAND, 0, S-BAND, S)).resize((pw, S-Y0-R+0), Image.LANCZOS) if False else None
    # platform surface: crop of deck centre
    surf = pt.crop((BAND+2, 0, BAND+2+pw, S-(Y0+R)))
    img.paste(surf, (X0+R, Y0+R))
    # rails: left, right, top (the free end)
    railcol = {'Scrapper': (108, 80, 54), 'Industrial': p['hz'], 'Modern': p['red'], 'Futuristic': p['white']}[look]
    def post(x, y):
        pc = {'Scrapper': (90, 66, 46), 'Industrial': p['dark'], 'Modern': p['zinc'], 'Futuristic': p['grey']}[look]
        bar(img, (x-7, y-7, x+8, y+8), pc, 'h', 1.35, .65, seed=x+y)
        if look == 'Futuristic': d.rectangle((x-2, y-2, x+2, y+2), fill=p['cyan']+(255,))
    bar(img, (X0+3, Y0+3, X0+R+1, S), railcol, 'h', 1.3, .66, grain='v' if look == 'Scrapper' else None, seed=1)
    bar(img, (X1-R-1, Y0+3, X1-3, S), railcol, 'h', 1.3, .66, grain='v' if look == 'Scrapper' else None, seed=2)
    bar(img, (X0+3, Y0+3, X1-3, Y0+R+1), railcol, 'v', 1.3, .66, grain='h' if look == 'Scrapper' else None, seed=3)
    if look == 'Industrial':
        for k in range(Y0+3, S, 24): d.rectangle((X0+3, k, X0+R, k+11), fill=p['black']+(255,)); d.rectangle((X1-R-1, k, X1-4, k+11), fill=p['black']+(255,))
        for k in range(X0+3, X1-3, 24): d.rectangle((k, Y0+3, k+11, Y0+R), fill=p['black']+(255,))
    if look == 'Futuristic':
        d.line((X0+8, Y0+8, X0+8, S), fill=p['cyan']+(255,), width=2); d.line((X1-9, Y0+8, X1-9, S), fill=p['cyan']+(255,), width=2); d.line((X0+8, Y0+8, X1-9, Y0+8), fill=p['cyan']+(255,), width=2)
    if look == 'Scrapper':
        for k in range(Y0+20, S, 50):
            for xx in (X0+3, X1-R-1): d.rectangle((xx, k, xx+R-2, k+5), fill=p['rope']+(255,))
    for (x, y) in [(X0+8, Y0+8), (X1-9, Y0+8), (X0+8, 140), (X1-9, 140), (X0+8, 248), (X1-9, 248)]: post(x, y)
    # clean outside platform
    a = np.asarray(img).copy(); a[:, :X0, 3] = 0; a[:, X1:, 3] = 0; a[:Y0, :, 3] = 0
    return Image.fromarray(a, 'RGBA')

# ---------------------------------------------------------------- driver
def build(look):
    out = {}
    out['RM_SuspensionDeck'] = deck(look)
    out['RM_SuspensionDeckGrated'] = grated(look)
    out['RM_SuspensionRailing_Edge'] = rail(look)
    an = anchor_north(look)
    out['RM_SuspensionAnchor_north'] = an
    out['RM_SuspensionAnchor_east'] = an.rotate(-90)
    out['RM_SuspensionAnchor_south'] = an.rotate(180)
    out['RM_SuspensionTower'] = tower(look)
    out['RM_SuspensionWreck'] = wreck(look)
    j = jetty_north(look)
    out['RM_SuspensionJetty_north'] = j
    out['RM_SuspensionJetty_east'] = j.rotate(-90)
    out['RM_SuspensionJetty_south'] = j.rotate(180)
    return out

if __name__ == '__main__':
    root = sys.argv[1]
    looks = sys.argv[2:] or LOOKS
    for look in looks:
        os.makedirs(os.path.join(root, look), exist_ok=True)
        for n, im in build(look).items():
            im.save(os.path.join(root, look, n + '.png'))
        print('wrote', look, flush=True)
