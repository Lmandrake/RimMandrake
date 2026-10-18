#!/usr/bin/env python3
"""Lake floor preview (LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP, plan P11; owner R11 2026-10-17).

    python3 src/RimMandrake/FlowWorks/Tools/lake_floor_preview.py [out_dir]

Builds the FlowWorks SelfTest (Windows dotnet.exe), runs its `--lake-floors` mode, which runs the PRODUCTION floor generator
(Source/RM_LakeFloorMath.cs, shipped defaults) over eight synthetic lakes from plains to chasm country, and renders each to
a PNG: a top view with depth contours, a cross-section through the deepest square, and a caption panel. Writes
index.html beside them with the roughness table. Default out_dir: Transient/fw_scenes/lake_floors/.

Nothing here computes a floor: the numbers are the C# generator's, so the picture cannot drift from the game.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
sys.path.insert(0, UTILS)

import selftest_flowworks_stock as stock_wrapper  # noqa: E402
from selftest_winstage import windows_project_path, stage_name_for  # noqa: E402
import winbuild  # noqa: E402

SQUARE_M = 2 ** 0.5   # a square is 2 m2: about 1.41 m on a side


def run_generator(json_path_unused=None):
    dotnet = stock_wrapper._find_dotnet()
    if dotnet is None:
        sys.exit("dotnet.exe not found; UNMEASURED")
    real = os.path.realpath(stock_wrapper.CSPROJ)
    if real.startswith("/mnt/"):
        stage_dir = os.path.dirname(real)
    else:
        stage_dir = os.path.join(winbuild.BUILD_ROOT, stage_name_for(real, winbuild.ROOT),
                                 os.path.relpath(os.path.dirname(real), winbuild.ROOT))
    with stock_wrapper.dotnet_lock():
        proj = windows_project_path(stock_wrapper.CSPROJ)
        b = subprocess.run([dotnet, "build", proj, "-c", "Release", "-nologo", "-v", "q", "-nodeReuse:false",
                            "-p:UseSharedCompilation=false"], capture_output=True, text=True)
        if b.returncode != 0:
            print(b.stdout[-2000:], b.stderr[-2000:])
            sys.exit("selftest build failed")
        dll = stock_wrapper._to_windows_path(os.path.join(stage_dir, "bin", "Release", "net8.0", "RimMandrakeFlowWorks.SelfTest.dll"))
        out = os.path.join(stage_dir, "lake_floors.json")
        r = subprocess.run([dotnet, dll, "--lake-floors", stock_wrapper._to_windows_path(out)], capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:])
            sys.exit("generator run failed")
        with open(out, encoding="utf-8") as fh:
            return json.load(fh)


def render(lake, path):
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    w, h = lake["w"], lake["h"]
    depth = np.full((h, w), np.nan)
    raw = np.full((h, w), np.nan)
    for c, f, f0 in zip(lake["cells"], lake["floor"], lake["floorNoWayOut"]):
        depth[c // w, c % w] = f / 2.0
        raw[c // w, c % w] = f0 / 2.0
    zs, xs = np.where(~np.isnan(depth))
    z0, z1, x0, x1 = zs.min() - 2, zs.max() + 3, xs.min() - 2, xs.max() + 3
    d = depth[z0:z1, x0:x1]
    r0 = raw[z0:z1, x0:x1]
    deepest = float(np.nanmax(d))
    iz, ix = np.unravel_index(np.nanargmax(d), d.shape)

    bg, ink, land = "#f3ead9", "#3b2a1a", "#d9c7a3"
    fig = plt.figure(figsize=(13, 5.2), dpi=110, facecolor=bg)
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.45, 0.9], wspace=0.5)
    ax = fig.add_subplot(gs[0, 0])
    ax.set_facecolor(land)
    cmap = matplotlib.colormaps["YlGnBu"]
    vmax = max(4.0, deepest)
    im = ax.imshow(d, cmap=cmap, vmin=0, vmax=vmax, origin="lower", interpolation="nearest")
    step = 0.5 if deepest <= 4 else (1 if deepest <= 8 else (2 if deepest <= 20 else 5))
    levels = np.arange(step, deepest + step, step)
    if len(levels) > 1:
        cs = ax.contour(np.nan_to_num(d, nan=0), levels=levels, colors=ink, linewidths=0.5, origin="lower")
        ax.clabel(cs, levels[::max(1, len(levels) // 5)], fmt="%g m", fontsize=6, colors=ink)
    ax.axhline(iz, color="#b5432a", lw=1, ls="--")
    ax.plot([ix], [iz], marker="x", color="#b5432a")
    ax.set_title("Top view: floor depth (contours every %g m)" % step, fontsize=9, color=ink)
    ax.set_xticks([]); ax.set_yticks([])
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
    cb.set_label("floor below ground (m)", fontsize=8, color=ink)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor(bg)
    row = d[iz, :]
    rrow = r0[iz, :]
    xm = np.arange(len(row)) * SQUARE_M
    floor = np.where(np.isnan(row), 0.0, row)
    rawf = np.where(np.isnan(rrow), 0.0, rrow)
    ax2.fill_between(xm, -floor, -max(deepest * 1.15, 3), step="mid", color="#8a6a45")
    ax2.fill_between(xm, 0, -floor, step="mid", where=~np.isnan(row), color="#7fb6d6", alpha=0.85)
    ax2.step(xm, -rawf, where="mid", color=ink, lw=0.8, ls=":", label="before the way-out pass")
    ax2.axhline(0, color=ink, lw=0.6)
    ax2.set_ylim(-max(deepest * 1.15, 3), 1)
    ax2.set_xlim(xm[0], xm[-1])
    width_m = (np.count_nonzero(~np.isnan(row))) * SQUARE_M
    exag = (width_m / max(deepest, 0.5)) / (ax2.get_window_extent().width / ax2.get_window_extent().height)
    ax2.set_title("Cross-section through the deepest square (vertical x%.0f)" % max(1, exag), fontsize=9, color=ink)
    ax2.set_xlabel("metres across", fontsize=8, color=ink)
    ax2.set_ylabel("metres below ground", fontsize=8, color=ink)
    ax2.tick_params(labelsize=7, colors=ink)
    ax2.legend(fontsize=7, loc="lower right", frameon=False)

    ax3 = fig.add_subplot(gs[0, 2])
    ax3.axis("off")
    cells = len(lake["cells"])
    litres = sum(lake["floor"]) * 1000
    text = [
        lake["title"],
        "",
        "biome: %s" % (lake["biome"] or "(none: hilliness only)"),
        "roughness %.2f  ->  band: %s" % (lake["roughness"], lake["band"]),
        "silted up: %s" % ("YES (deepest 2 to 2.5 m)" if lake["silted"] else "no"),
        "silt-flat bottom: %s" % ("no" if lake["siltCap"] >= 1 else "yes (levelled at %d%%)" % round(lake["siltCap"] * 100)),
        "shelves (terraces): %s" % (lake["terraces"] or "none"),
        "",
        "deepest drawn: %.1f m   recorded: %.1f m" % (lake["target"], deepest),
        "mean floor: %.1f m   squares: %s" % (sum(lake["floor"]) / 2.0 / cells, format(cells, ",")),
        "water when full: %s L" % format(litres, ","),
        "off-radial (>= 1 m): %d%% of deep squares" % round(lake["offRadial"] * 100),
        "way-out pass moved %d squares" % lake["wayOutMoved"],
        "one-basin pass silted %d squares" % lake.get("basinFilled", 0),
        "draw: %s" % ("the first at its seed" if not lake.get("skipped") else
                      "first %s draw after %d skipped" % (lake.get("want"), lake["skipped"])),
        "",
        "no shore shelf; way out 1 m (defaults)",
    ]
    ax3.text(0, 1, "\n".join(text), va="top", ha="left", fontsize=8.5, color=ink, family="DejaVu Sans")
    fig.savefig(path, facecolor=bg, bbox_inches="tight")
    plt.close(fig)
    return deepest


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "Transient", "fw_scenes", "lake_floors")
    os.makedirs(out_dir, exist_ok=True)
    data = run_generator()
    cards = []
    for i, lake in enumerate(data["lakes"]):
        name = "lake_%d.png" % (i + 1)
        deepest = render(lake, os.path.join(out_dir, name))
        cards.append((name, lake, deepest))
        print("%-45s deepest %5.1f m  %s" % (lake["title"], deepest, name))
    rows = "".join(
        "<tr><td>%s</td><td>%.2f</td><td>%g to %g m</td><td>%g m</td><td>%d%%</td><td>%d%%</td><td>%d%%</td><td>%d%%</td></tr>"
        % (b["name"], b["r"], b["low"], b["high"], b["cap"], round(b["silt"] * 100), round(b["siltFlat"] * 100),
           round(b["wall"] * 100), round(b["terrace"] * 100)) for b in data["bands"])
    figs = "".join(
        '<figure><img src="%s" alt="%s"><figcaption>%d. %s: deepest %.1f m</figcaption></figure>' % (n, l["title"], i + 1, l["title"], d)
        for i, (n, l, d) in enumerate(cards))
    html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lake Floor Variety</title>
<style>
:root{--bg:#f3ead9;--ink:#3b2a1a;--line:#c9b48d;--card:#fbf6ec}
@media (prefers-color-scheme: dark){:root{--bg:#2a2017;--ink:#efe3cc;--line:#6b5638;--card:#33271b}}
body{background:var(--bg);color:var(--ink);font:15px/1.5 Georgia,serif;margin:0;padding:16px;max-width:1300px;margin:auto}
table{border-collapse:collapse;margin:8px 0 20px;font-size:14px;display:block;overflow-x:auto}
td,th{border:1px solid var(--line);padding:4px 8px;text-align:left}
figure{background:var(--card);border:1px solid var(--line);margin:0 0 18px;padding:8px}
img{max-width:100%;height:auto;display:block}
</style></head><body>
<h1>Lake floor variety (P11, offline preview)</h1>
<p>Your ruling (R11): <i>"Vary it. Some lakes will be shallow and silted up. Others will be deep and chasm-like. Depends on
the biome. The more mountainous, the deeper in general. The more plains-like, the smoother/shallower. They should also have
some variation down there, not just a radial crater."</i></p>
<p>Eight lakes on made-up maps, floors drawn by the game's own floor code at the shipped defaults. A full lake looks
exactly as it does today; this is what the floor would show if the lake were drained. Each lake is one random draw from
its band. To show every kind once, each lake takes the first draw of the kind its caption names (silted or open; the
skipped draws are counted on the picture); the table below gives the real odds. Another lake in the same place could be
shallower or deeper.</p>
<h2>The roughness table (tuning; yours to approve)</h2>
<p>Roughness is the map tile's hilliness plus a nudge from the biome (swamps, sumps and plains shallower; canyons,
craters and mountains deeper). The deepest floor of a lake is drawn from the range, most lakes near the low end.</p>
<table><tr><th>band</th><th>roughness</th><th>deepest floor, per lake</th><th>never deeper</th><th>silted up</th>
<th>flat silt bottom</th><th>wall width (of the way to the middle)</th><th>shelves</th></tr>@@ROWS@@</table>
<p>Safety rule (a default you can veto): every floor square has a
walked way out with no step over 1 m, so a drained lake never traps a person (no shore shelf: owner 2026-10-18, drained means dry). A hole with no way down to the deep
water is silted up to its rim, so a drained lake never splits into pools.</p>
@@FIGS@@
</body></html>""".replace("@@ROWS@@", rows).replace("@@FIGS@@", figs)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print("wrote", os.path.join(out_dir, "index.html"))


if __name__ == "__main__":
    main()
