#!/usr/bin/env python3
"""Creature size-mismatch visual portfolio (MandrakeVisualize portfolio pass).

Reads creature_register_rows.json, derives the mismatch ratio against vanilla's own
fitted law, and renders three portfolio members + a contact sheet into review/viz/.

Measure: mismatch = max(drawSize) / (1.995 * bodySize^0.375)
         (vanilla RimWorld's OWN fitted law, n=66 vanilla animals+mechs, R2=0.71 --
          see design/Jawa/worldbuilding/creature_size_model.md section 2)
"""
import json, math, collections, statistics, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, FixedLocator
from matplotlib.lines import Line2D
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "creature_register_rows.json")
OUT = os.path.join(ROOT, "viz")
os.makedirs(OUT, exist_ok=True)

K, P = 1.995, 0.375
BAND_LO, BAND_HI = 0.67, 1.5          # vanilla's own scatter band (geometric sigma 1.22)
BROKEN_LO, BROKEN_HI = 0.40, 2.5
MIN_N = 6                              # smallest mod block we will characterise
FALSE_POSITIVES = {"VGE_Astronaut"}    # humanlike-proportioned; outside the animal law

INK   = "#1a1a1a"; GRID = "#d8d8d8"; MUTE = "#9a9a9a"
BIG   = "#b8531b"   # oversized  (warm, light-ish)
SMALL = "#1f4e79"   # undersized (cool, dark)
OK    = "#8d9296"
BLOCK_C = "#5c1f7a"; SCAT_C = "#a08800"

plt.rcParams.update({
    "font.size": 8.5, "axes.edgecolor": INK, "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})

# ---------------------------------------------------------------- load + derive
doc = json.load(open(SRC))
meta, rows = doc["meta"], doc["rows"]

def draw_cells(r):
    v = r.get("drawSize")
    if isinstance(v, list):
        vv = [x for x in v if isinstance(x, (int, float))]
        return max(vv) if vv else None
    return v if isinstance(v, (int, float)) else None

recs, excluded = [], collections.Counter()
for r in rows:
    bs, dc = r.get("bodySize"), draw_cells(r)
    if not bs:
        excluded["no bodySize (no mismatch ratio computable)"] += 1
        excluded.setdefault("_names", []) if False else None
        continue
    if not dc:
        excluded["no drawSize"] += 1
        continue
    recs.append(dict(
        defName=r["defName"], label=r["label"], mod=r["mod"], kind=r["kindOf"],
        bs=bs, dc=dc, ratio=dc / (K * bs ** P), cut=bool(r.get("cut")),
        vehicle=(r["kindOf"] == "vehicle"),
        fp=(r["defName"] in FALSE_POSITIVES),
    ))
NO_BS = [r["defName"] for r in rows if not r.get("bodySize")]
live = [x for x in recs if not x["cut"] and not x["fp"]]
cut  = [x for x in recs if x["cut"]]

def outb(x): return x["ratio"] > BAND_HI or x["ratio"] < BAND_LO

# per-mod block statistics (live only -- CUT creatures need no intervention)
by_mod = collections.defaultdict(list)
for x in live: by_mod[x["mod"]].append(x)
blocks = []
for m, v in by_mod.items():
    if len(v) < MIN_N: continue
    med = statistics.median(x["ratio"] for x in v)
    out = [x for x in v if outb(x)]
    after = sum(1 for x in v if (x["ratio"] / med) > BAND_HI or (x["ratio"] / med) < BAND_LO)
    fixed = (len(out) - after) / len(out) if out else 0.0
    lo = sorted(v, key=lambda x: x["bs"])[: len(v) // 2]
    hi = sorted(v, key=lambda x: x["bs"])[len(v) // 2 :]
    blocks.append(dict(mod=m, n=len(v), med=med, n_out=len(out), n_after=after,
                       fixed=fixed, vehicles=all(x["vehicle"] for x in v),
                       med_lo=statistics.median(x["ratio"] for x in lo),
                       med_hi=statistics.median(x["ratio"] for x in hi),
                       pts=[x["ratio"] for x in v]))
blocks.sort(key=lambda b: b["med"], reverse=True)
BLOCKY = {b["mod"] for b in blocks if b["n_out"] >= 3 and b["fixed"] >= 0.60}

TOT_OUT   = sum(b["n_out"] for b in blocks)
TOT_AFTER = sum(b["n_after"] for b in blocks)

SRC_LINE = (f"Source: creature_register_rows.json, {meta['dumpMods']}-mod def dump "
            f"{meta['dumpCaptured'][:10]} | law: RimWorld Core, n=66, R2=0.71")
BASIS = ("Comparability basis: mismatch = max(drawSize) / (1.995 x bodySize^0.375), i.e. each creature is\n"
         "measured against what VANILLA itself draws at that mass, so vanilla's deliberate small-animal\n"
         "inflation (~6x at bodySize 0.2) is already divided out. Residual drift across mass octiles is\n"
         "1.15 -> 0.98 -> 1.21 (median), i.e. within the vanilla band -- ratios ARE comparable across the mass range.")
EXCL = (f"Excluded: {len(NO_BS)} creatures with no bodySize ({', '.join(NO_BS)}) have no ratio at all; "
        f"VGE_Astronaut (humanlike-proportioned mech) is a known law false-positive.")

def _wrap(t, w):
    import textwrap
    return "\n".join(textwrap.fill(l, w) for l in t.split("\n"))

# ================================================================= MEMBER 1
def fig1():
    fig, ax = plt.subplots(figsize=(9.4, 7.8))
    xs = np.logspace(math.log10(0.008), math.log10(45), 200)
    ax.fill_between(xs, K*xs**P*BAND_LO, K*xs**P*BAND_HI, color="#e9edf2", zorder=0,
                    label="vanilla's own scatter (0.67x-1.5x)")
    ax.plot(xs, K*xs**P, color=INK, lw=1.6, zorder=3)

    cx = [x["bs"] for x in cut]; cy = [x["dc"] for x in cut]
    ax.scatter(cx, cy, s=9, facecolors="none", edgecolors="#c9c9c9", lw=0.5, zorder=1)
    grp = {"in": [], "big": [], "small": []}
    for x in live:
        grp["big" if x["ratio"] > BAND_HI else "small" if x["ratio"] < BAND_LO else "in"].append(x)
    ax.scatter([x["bs"] for x in grp["in"]], [x["dc"] for x in grp["in"]],
               s=13, c=OK, alpha=.55, lw=0, zorder=2)
    for key, col, mk in (("big", BIG, "^"), ("small", SMALL, "v")):
        ve = [x for x in grp[key] if x["vehicle"]]; an = [x for x in grp[key] if not x["vehicle"]]
        ax.scatter([x["bs"] for x in an], [x["dc"] for x in an], s=26, c=col, marker=mk,
                   lw=0, zorder=4)
        ax.scatter([x["bs"] for x in ve], [x["dc"] for x in ve], s=42, facecolors="none",
                   edgecolors=col, marker="s", lw=1.1, zorder=5)

    # merge co-located extremes into one label so annotations cannot overprint (render-QA D1)
    picks = sorted(live, key=lambda z: -z["ratio"])[:6] + sorted(live, key=lambda z: z["ratio"])[:4]
    merged = {}
    for x in picks:
        merged.setdefault((round(x["bs"], 4), round(x["dc"], 4)), []).append(x)
    items = sorted(merged.items(), key=lambda kv: -kv[1][0]["ratio"])
    OFFS_BIG = [(14, 10), (16, 26), (16, -20), (16, 42), (16, -34), (16, 56)]
    OFFS_SML = [(-14, -22), (-16, -38), (-16, 20), (-16, -54), (-16, 36)]
    ib = isml = 0
    for (bx_, dy_), grp_ in items:
        nm = " / ".join(sorted(g["label"] for g in grp_))
        if len(nm) > 34: nm = nm[:32] + "..."
        r0 = grp_[0]["ratio"]
        if r0 > 1:
            off = OFFS_BIG[ib % len(OFFS_BIG)]; ib += 1; ha = "left"
        else:
            off = OFFS_SML[isml % len(OFFS_SML)]; isml += 1; ha = "right"
        ax.annotate(f"{nm}  {r0:.2f}x", (bx_, dy_), textcoords="offset points",
                    xytext=off, fontsize=7.2, ha=ha,
                    color=BIG if r0 > 1 else SMALL,
                    bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="none", alpha=.86),
                    arrowprops=dict(arrowstyle="-", lw=.5, shrinkA=0, shrinkB=2,
                                    color=BIG if r0 > 1 else SMALL, alpha=.65))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.007, 50); ax.set_ylim(0.35, 30)
    ax.set_xlabel("bodySize  (= mass in kg-equivalent; StatDefOf.Mass base 1)")
    ax.set_ylabel("drawSize  (rendered quad, map cells)")
    ax.grid(True, which="both", color=GRID, lw=.4, zorder=0)
    _pct = 100 * len(grp["in"]) / len(live)
    _n_in, _n_live = len(grp["in"]), len(live)
    ax.set_title("%.0f%% of live modded creatures (%d of %d) obey the engine's own size law --\n"
                 "the defect is a minority of points, and it runs in BOTH directions"
                 % (_pct, _n_in, _n_live),
                 fontsize=11.5, loc="left", pad=10, weight="bold")
    ax.xaxis.set_minor_formatter(NullFormatter()); ax.yaxis.set_minor_formatter(NullFormatter())
    ax.text(0.985, 0.03, "log-log: both axes are ratio scales, so the power law is a straight line",
            transform=ax.transAxes, ha="right", fontsize=7, color=MUTE, style="italic")
    hs = [Line2D([], [], color=INK, lw=1.6, label="vanilla law  drawSize = 1.995 x bodySize^0.375  (n=66 vanilla defs)"),
          Line2D([], [], marker="s", ls="", mfc="#e9edf2", mec="#e9edf2", ms=9, label="vanilla's own scatter band, 0.67x-1.5x"),
          Line2D([], [], marker="o", ls="", color=OK, ms=5, label=f"live creature in band (n={len(grp['in'])})"),
          Line2D([], [], marker="^", ls="", color=BIG, ms=6, label=f"drawn TOO BIG for its mass (n={len(grp['big'])})"),
          Line2D([], [], marker="v", ls="", color=SMALL, ms=6, label=f"drawn TOO SMALL for its mass (n={len(grp['small'])})"),
          Line2D([], [], marker="s", ls="", mfc="none", mec=INK, ms=7, label="vehicle -- outside vanilla's fitted population, shown but disclosed"),
          Line2D([], [], marker="o", ls="", mfc="none", mec="#c9c9c9", ms=5, label=f"already CUT by Cherry Picker, needs no fix (n={len(cut)})")]
    ax.legend(handles=hs, loc="upper left", fontsize=7.2, frameon=False, borderpad=0.2, labelspacing=0.5)
    fig.text(.062, .155, BASIS, fontsize=6.6, color="#444", va="top", linespacing=1.5)
    fig.text(.062, .058, _wrap(EXCL + "  " + SRC_LINE, 128), fontsize=6.4, color=MUTE,
             va="top", linespacing=1.5)
    fig.subplots_adjust(left=.072, right=.985, top=.895, bottom=.275)
    for e in ("png", "svg"): fig.savefig(f"{OUT}/fig1_size_law_scatter.{e}", dpi=170)
    plt.close(fig)

# ================================================================= MEMBER 2
def fig2():
    n = len(blocks)
    H = 0.34 * n + 5.2
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.4, H),
                                 gridspec_kw=dict(width_ratios=[2.5, 1], wspace=.30))
    y = np.arange(n)[::-1]
    ax.axvspan(BAND_LO, BAND_HI, color="#e9edf2", zorder=0)
    ax.axvline(1.0, color=INK, lw=1.0, zorder=1)
    for i, b in zip(y, blocks):
        pts = b["pts"]
        col = BIG if b["med"] > BAND_HI else SMALL if b["med"] < BAND_LO else "#3d3d3d"
        jit = (np.random.default_rng(7 + i).random(len(pts)) - .5) * .30
        ax.scatter(pts, np.full(len(pts), i) + jit, s=9,
                   c=[BIG if p > BAND_HI else SMALL if p < BAND_LO else OK for p in pts],
                   alpha=.62, lw=0, zorder=3)
        q = statistics.quantiles(pts, n=4) if len(pts) > 3 else [min(pts), b["med"], max(pts)]
        ax.plot([q[0], q[2]], [i, i], color=INK, lw=1.5, alpha=.75, zorder=4)
        ax.plot([b["med"]], [i], marker="|", ms=13, mew=2.2, color=col, zorder=5)
    labs = [(b["mod"][:31] + "..." if len(b["mod"]) > 34 else b["mod"]) +
            f"  (n={b['n']})" + ("  [vehicles]" if b["vehicles"] else "") for b in blocks]
    ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=7.4)
    ax.set_ylim(-.9, n - .1)
    ax.set_xscale("log"); ax.set_xlim(0.3, 5.0)
    ax.xaxis.set_major_locator(FixedLocator([0.4, 0.67, 1, 1.5, 2.5, 4]))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xticklabels(["0.4x", "0.67x", "1x", "1.5x", "2.5x", "4x"])
    ax.set_xlabel("mismatch ratio  (drawn size / vanilla-predicted size for that mass; log scale)")
    ax.grid(True, axis="x", which="major", color=GRID, lw=.4, zorder=0)
    ax.set_title("Provenance explains most of it: whole mods sit off-centre, and for six of them\n"
                 "one block-level multiplier clears most of the damage -- but not for all",
                 fontsize=12, loc="left", pad=12, weight="bold")

    # right panel: block-fix efficacy. Only meaningful where a mod has >=3 out-of-band creatures.
    for i, b in zip(y, blocks):
        if b["n_out"] >= 3:
            bx.barh([i], [100 * max(b["fixed"], 0)],
                    color=BLOCK_C if b["mod"] in BLOCKY else SCAT_C, height=.62, zorder=2)
            if b["fixed"] > 0:
                bx.text(102, i, f"{100*b['fixed']:.0f}%", va="center", fontsize=6.9, color=INK)
            else:
                bx.text(2, i, "a block edit would make it worse", va="center",
                        fontsize=6.6, color=MUTE, style="italic")
        else:
            bx.text(2, i, "too few out of band to characterise", va="center",
                    fontsize=6.6, color=MUTE, style="italic")
        bx.text(-4, i, f"{b['n_out']}", va="center", ha="right", fontsize=6.9,
                color=INK if b["n_out"] else MUTE)
    bx.set_yticks([]); bx.set_ylim(-.9, n - .1); bx.set_xlim(0, 118)
    bx.set_xticks([0, 50, 100]); bx.set_xticklabels(["0%", "50%", "100%"])
    bx.set_xlabel("% of that mod's out-of-band creatures that ONE\nblock-level multiplier would bring back in band")
    bx.grid(True, axis="x", color=GRID, lw=.4, zorder=0)
    bx.text(-4, n - .2, "out of\nband", ha="right", va="bottom", fontsize=6.6, color=MUTE)
    bx.legend(handles=[Line2D([], [], color=BLOCK_C, lw=7, label="BLOCK defect -- one mod-level edit"),
                       Line2D([], [], color=SCAT_C, lw=7, label="SCATTERED -- per-creature work")],
              loc="lower left", bbox_to_anchor=(0.0, 1.012), fontsize=7.2, frameon=False, ncol=1)

    foot1 = ("Every creature is drawn as a point, not just a summary, so a mod's median cannot hide its spread. "
             "Confound checked: within each mod the median is stable across that mod's OWN low-mass and high-mass halves "
             "(Vanilla Vehicles Expanded 1.72x / 1.59x; Biomes! Caverns 0.85x / 0.94x; Alpha Animals 1.36x / 1.08x), so a mod's "
             "offset is an authoring choice, not an artefact of which mass range it happens to populate.")
    fig.text(.030, 0.098, _wrap(foot1, 175) + "\n" + _wrap(BASIS.replace("\n", " "), 175),
             fontsize=6.6, color="#444", va="top", linespacing=1.55)
    foot2 = (f"Live (uncut) creatures only, mods with n>={MIN_N}; a creature already cut by Cherry Picker needs no fix. "
             f"{TOT_OUT} live creatures in these blocks are out of band; a per-mod block multiplier would clear "
             f"{TOT_OUT-TOT_AFTER} of them ({100*(TOT_OUT-TOT_AFTER)/TOT_OUT:.0f}%), leaving {TOT_AFTER} that need individual edits. "
             + EXCL + "  " + SRC_LINE)
    fig.text(.030, 0.028, _wrap(foot2, 175), fontsize=6.4, color=MUTE, va="top", linespacing=1.55)
    fig.subplots_adjust(left=.205, right=.955, top=1 - 1.45 / H, bottom=1.55 / H + .095)
    for e in ("png", "svg"): fig.savefig(f"{OUT}/fig2_mismatch_by_mod.{e}", dpi=170)
    plt.close(fig)

# ================================================================= MEMBER 3
def fig3(topn=32):
    pool = [x for x in live if outb(x)]
    worst = sorted(pool, key=lambda x: -abs(math.log(x["ratio"])))[:topn]
    worst.sort(key=lambda x: x["ratio"])
    n = len(worst)
    H = 0.315 * n + 4.3
    fig, ax = plt.subplots(figsize=(11.6, H))
    y = np.arange(n)
    ax.axvspan(BAND_LO, BAND_HI, color="#e9edf2", zorder=0)
    ax.axvline(1.0, color=INK, lw=1.2, zorder=2)
    for i, x in zip(y, worst):
        col = BIG if x["ratio"] > 1 else SMALL
        ax.plot([1.0, x["ratio"]], [i, i], color=col, lw=1.5, alpha=.55, zorder=3)
        ax.plot([x["ratio"]], [i], "o", ms=7, color=col,
                mec=BLOCK_C if x["mod"] in BLOCKY else SCAT_C, mew=1.7, zorder=4)
        ax.text(x["ratio"] * (1.06 if x["ratio"] > 1 else 0.94), i,
                f"{x['ratio']:.2f}x", va="center", ha="left" if x["ratio"] > 1 else "right",
                fontsize=6.9, color=col, weight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(
        [("[BLOCK FIX] " if x["mod"] in BLOCKY else "[hand fix]  ")
         + f"{x['label']}  ({x['mod'][:28]})   bodySize {x['bs']:g} -> drawSize {x['dc']:g}"
         for x in worst], fontsize=7.1)
    for t, x in zip(ax.get_yticklabels(), worst):
        t.set_color(BLOCK_C if x["mod"] in BLOCKY else "#6b5a00")
    ax.set_xscale("log"); ax.set_xlim(0.33, 5.6); ax.set_ylim(-.8, n - .2)
    ax.xaxis.set_major_locator(FixedLocator([0.4, 0.67, 1, 1.5, 2.5, 4]))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xticklabels(["0.4x", "0.67x", "1x\nvanilla", "1.5x", "2.5x", "4x"])
    ax.set_xlabel("mismatch ratio -- stems run from 1.0x, the size vanilla would draw at that mass\n"
                  "(log scale, so equal stem lengths are equal ratios)")
    ax.grid(True, axis="x", color=GRID, lw=.4, zorder=0)
    ax.set_title(f"The actual worklist: the {n} live creatures furthest off vanilla's law --\n"
                 "tagged by whether a mod-level edit or a hand edit is the cheaper fix",
                 fontsize=12, loc="left", pad=12, weight="bold")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=BIG, ms=6.5, label="drawn too big for its mass"),
                       Line2D([], [], marker="o", ls="", color=SMALL, ms=6.5, label="drawn too small for its mass"),
                       Line2D([], [], marker="o", ls="", mfc="white", mec=BLOCK_C, mew=1.8, ms=7.5,
                              label="[BLOCK FIX] its mod is a block defect"),
                       Line2D([], [], marker="o", ls="", mfc="white", mec=SCAT_C, mew=1.8, ms=7.5,
                              label="[hand fix] its mod is scattered")],
              loc="lower right", fontsize=7.2, frameon=True, framealpha=.95, edgecolor=GRID)
    n_cut_out = len([x for x in cut if outb(x) and not x["fp"]])
    foot = (f"Live (uncut) creatures only: a creature already cut by Cherry Picker needs no fix, and {n_cut_out} of the "
            f"{len(pool)+n_cut_out} out-of-band creatures in the register are already cut -- including most of the Jurassic dinosaur block. "
            f"Ranked by |log ratio| so a 0.44x undersize and a 2.3x oversize rank on the same footing. "
            f"{len(pool)} live creatures are out of band in total; "
            f"{len([x for x in live if x['ratio']>BROKEN_HI or x['ratio']<BROKEN_LO])} are past the 'broken' threshold (>2.5x or <0.4x). "
            "Which field to edit -- bodySize (mass, yield, haul, shootability) or drawSize (the sprite only) -- is a design call per "
            "creature; this figure diagnoses, it does not prescribe. " + EXCL + "  " + SRC_LINE)
    fig.text(.030, 0.075, _wrap(foot, 168), fontsize=6.5, color="#444", va="top", linespacing=1.55)
    fig.subplots_adjust(left=.385, right=.965, top=1 - 1.15 / H, bottom=1.55 / H + .04)
    for e in ("png", "svg"): fig.savefig(f"{OUT}/fig3_worklist.{e}", dpi=170)
    plt.close(fig)

fig1(); fig2(); fig3()

# ================================================================= contact sheet
from PIL import Image
ims = [Image.open(f"{OUT}/{f}.png").convert("RGB") for f in
       ("fig1_size_law_scatter", "fig2_mismatch_by_mod", "fig3_worklist")]
W = max(i.width for i in ims)
HDR = 96
ims = [i.resize((W, round(i.height * W / i.width)), Image.LANCZOS) for i in ims]
sheet = Image.new("RGB", (W, HDR + sum(i.height for i in ims) + 24 * len(ims)), "white")
from PIL import ImageDraw, ImageFont
dr = ImageDraw.Draw(sheet)
try:
    f1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
except OSError:
    f1 = f2 = ImageFont.load_default()
dr.text((34, 22), "Creature size mismatch -- visual portfolio (3 members)", font=f1, fill=(20, 20, 20))
dr.text((34, 60), "Which creatures need intervention, and is the defect systematic by provenance or scattered per-creature?",
        font=f2, fill=(90, 90, 90))
yy = HDR
for i in ims:
    sheet.paste(i, (0, yy)); yy += i.height + 24
sheet.save(f"{OUT}/contact_sheet.png", quality=92)

print("OUT", OUT)
print("live", len(live), "cut", len(cut), "out-of-band live", len([x for x in live if outb(x)]))
print("blocks", len(blocks), "BLOCKY", sorted(BLOCKY))
print("TOT_OUT", TOT_OUT, "AFTER", TOT_AFTER)
for f in sorted(os.listdir(OUT)):
    print(" ", f, os.path.getsize(os.path.join(OUT, f)))
