#!/usr/bin/env python3
"""FAUNA_LORE_DIVERSIFICATION_1: the divergence manifest is sound and the graph regenerates.

1. The committed manifest passes fauna_divergence_graph.check (every row off the 12-15 band in
   its stated direction, ruled_best = K x bodySize, a reason, the delegated-judge ruling, a
   defName present in the roster snapshot).
2. Every manifest row traces to an accept/adjust verdict in the committed judge record, with the
   same K; no rejected row slipped in.
3. Planted faults are caught (in-band K, wrong direction, unknown defName, missing ruling) —
   the checker can see.
4. The graph draws to a temp PNG of plausible size, and the drawn figure (captured at savefig)
   (inspected at the moment of saving) carries every manifest row, with real visible markers: red/green scatter points exactly at (bodySize, ruled_best), each
   off the band, and an annotation naming every defName at its own point.
5. Every reason is '<description clause>; <art clause>': the art clause names the art, and the
   description clause shares a content word with the description the judge was given.
"""
import csv
import io
import math
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fauna_divergence_graph as g  # noqa: E402

JUDGE_INPUT = os.path.join(g.ROOT, "design", "Jawa", "worldbuilding", "fauna_lore_divergence_2026-11-02",
                           "judge_input.csv")
VERDICT = os.path.join(g.ROOT, "design", "Jawa", "worldbuilding", "fauna_lore_divergence_2026-11-02",
                       "judge_verdict.md")


STOP = {"about", "above", "after", "again", "against", "among", "being", "below", "between", "could",
        "every", "other", "their", "there", "these", "those", "through", "under", "until", "which",
        "while", "would", "where", "whose", "though", "often", "still", "since", "known", "species",
        "creature", "creatures", "animal", "animals"}


def _words(s):
    return set(re.findall(r"[a-z]{5,}", s.lower())) - STOP


def reason_findings(manifest, descriptions):
    """A reason must point at evidence a player can see and read: '<description>; <art ...>'."""
    bad = []
    for r in manifest:
        d, reason = r["defName"], r.get("reason", "")
        m = re.match(r"^(.+?);\s*(.*\bart\b.*)$", reason)
        if not m:
            bad.append("%s: reason %r is not '<description clause>; <art clause>'" % (d, reason))
            continue
        desc, art = m.group(1), m.group(2)
        if len(desc.split()) < 2 or len(art.split()) < 3:
            bad.append("%s: reason clauses too thin (%r / %r)" % (d, desc, art))
        if not _words(desc) & _words(descriptions.get(d, "")):
            bad.append("%s: description clause %r shares no word with the judged description" % (d, desc))
    return bad


def _closed(path):
    from matplotlib.path import Path
    if path.codes is not None and Path.CLOSEPOLY in path.codes:
        return True
    v = path.vertices
    return len(v) > 2 and tuple(v[0]) == tuple(v[-1])


def figure_findings(manifest, fig):
    """The drawn figure must show every divergence as a labeled, off-band point."""
    from matplotlib.colors import to_hex, to_rgba
    bad = []
    ax = fig.axes[0]
    colours = {"terror": "#c0392b", "harmless": "#1e8449"}
    want = {k: sorted((round(float(r["bodySize"]), 4), round(float(r["ruled_best"]), 4))
                      for r in manifest if r["direction"] == k) for k in colours}
    got = {k: [] for k in colours}
    for coll in ax.collections:
        fc, offs = coll.get_facecolors(), coll.get_offsets()
        if len(fc) == 0 or not coll.get_visible() or (coll.get_alpha() is not None and coll.get_alpha() < 0.5):
            continue  # a hidden or near-transparent collection shows nothing: its points do not count
        if min(float(c[3]) for c in fc) < 0.5:
            continue
        sizes, paths = coll.get_sizes(), coll.get_paths()
        if len(sizes) == 0 or min(float(z) for z in sizes) < 4 or not paths \
                or any(len(pth.vertices) == 0 for pth in paths):
            continue  # zero-size or empty markers draw nothing
        lws = coll.get_linewidths()
        if not all(_closed(pth) for pth in paths) and (len(lws) == 0 or max(float(w) for w in lws) <= 0):
            continue  # an unfilled marker (x, +) with no line width draws nothing
        for i, (x, y) in enumerate(offs):  # each point's own colour (a single fc broadcasts)
            hexc = to_hex(fc[i if len(fc) > 1 else 0], keep_alpha=False)
            for k, c in colours.items():
                if hexc == c:
                    got[k].append((round(float(x), 4), round(float(y), 4)))
    # the shaded band the reader sees must be the 12-15 x bodySize band the points are judged against
    band = [c for c in ax.collections if "band" in str(c.get_label()).lower()]
    if len(band) != 1 or not band[0].get_visible():
        bad.append("graph: expected one visible shaded band, found %d" % len(band))
    else:
        ks = set()
        for pth in band[0].get_paths():
            for vx, vy in pth.vertices:
                if vx > 0:
                    ks.add(round(float(vy) / float(vx), 3))
        if ks != {g.K_LO, g.K_HI}:
            bad.append("graph: shaded band edges at K %s, not {%g, %g}" % (sorted(ks), g.K_LO, g.K_HI))
    (x0, x1), (y0, y1) = sorted(ax.get_xlim()), sorted(ax.get_ylim())
    for k in colours:
        for x, y in got[k]:
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                bad.append("graph: %s point (%g, %g) lies outside the axes limits (clipped)" % (k, x, y))
        if sorted(got[k]) != want[k]:
            bad.append("graph: %s points drawn %d != manifest %d (or misplaced)"
                       % (k, len(got[k]), len(want[k])))
        for x, y in got[k]:
            if (k == "terror" and not y > g.K_HI * x) or (k == "harmless" and not y < g.K_LO * x):
                bad.append("graph: %s point (%g, %g) not drawn on its side of the band" % (k, x, y))
    fig.canvas.draw()  # lay out text so its rendered extent is real
    renderer = fig.canvas.get_renderer()
    fig_w, fig_h = fig.bbox.width, fig.bbox.height
    labelled = {}
    for t in ax.texts:
        xy = getattr(t, "xy", None)
        if xy is None or not t.get_visible() or (t.get_alpha() is not None and t.get_alpha() < 0.5) \
                or float(to_rgba(t.get_color())[3]) < 0.5:
            continue  # an invisible label labels nothing
        # where the text actually renders: on the canvas and beside its anchor, not merely anchored
        bb = t.get_window_extent(renderer)
        ax_xy = ax.transData.transform((float(xy[0]), float(xy[1])))
        on_canvas = bb.x0 >= 0 and bb.y0 >= 0 and bb.x1 <= fig_w and bb.y1 <= fig_h
        near = (bb.x0 - 60 <= ax_xy[0] <= bb.x1 + 60) and (bb.y0 - 30 <= ax_xy[1] <= bb.y1 + 30)
        if t.get_clip_on() and (t.get_clip_box() is not None or t.get_clip_path() is not None):
            # matplotlib clips text only when clip_on AND a clip region is set; then it must fit inside
            box = t.get_clip_box() or ax.bbox
            on_canvas = on_canvas and bb.x0 >= box.x0 and bb.y0 >= box.y0 and bb.x1 <= box.x1 and bb.y1 <= box.y1
        if not (on_canvas and near):
            bad.append("graph: label %r renders away from its point or off the canvas" % t.get_text())
            continue
        for name in t.get_text().split(" / "):
            labelled[name.strip()] = (round(float(xy[0]), 4), round(float(xy[1]), 4))
    for r in manifest:
        at = labelled.get(r["defName"])
        if at is None:
            bad.append("graph: %s not labeled" % r["defName"])
        elif at != (round(float(r["bodySize"]), 4), round(float(r["ruled_best"]), 4)):
            bad.append("graph: %s labeled at %s, not its ruled point" % (r["defName"], at))
    return bad


def draw_and_capture(manifest, roster, out):
    """Run g.draw unchanged; inspect the Figure AT the moment it is saved (what the PNG holds).
    Returns the findings from the last save, or None when draw saved nothing."""
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib.figure import Figure
    at_save = []
    orig = Figure.savefig

    def spy(self, *a, **k):
        target = a[0] if a else k.get("fname")
        if isinstance(target, (str, os.PathLike)) and os.path.abspath(target) == os.path.abspath(out):
            at_save.append(figure_findings(manifest, self))  # only the save that writes OUR png counts
        return orig(self, *a, **k)

    Figure.savefig = spy
    try:
        g.draw(manifest, roster, out)
    finally:
        Figure.savefig = orig
    return at_save[-1] if at_save else None


def main():
    fails = []
    manifest, roster = g.load(g.MANIFEST), g.load(g.ROSTER)
    bad = g.check(manifest, roster)
    fails += ["manifest: " + b for b in bad]
    if len(manifest) < 10:
        fails.append("manifest has only %d rows" % len(manifest))

    text = open(VERDICT, encoding="utf-8").read()
    body = text.split("```csv", 1)[1].split("```", 1)[0].strip()
    verdict = {r["defName"]: r for r in csv.DictReader(io.StringIO(body))}
    if len(verdict) < 30:
        fails.append("judge verdict parsed only %d rows" % len(verdict))
    for r in manifest:
        v = verdict.get(r["defName"])
        if not v:
            fails.append("%s: no judge verdict" % r["defName"])
        elif v["verdict"] not in ("accept", "adjust"):
            fails.append("%s: judge said %s" % (r["defName"], v["verdict"]))
        elif not (math.isfinite(float(v["K_final"])) and math.isfinite(float(r["K_ruled"]))) \
                or abs(float(v["K_final"]) - float(r["K_ruled"])) > 1e-6:
            fails.append("%s: K %s != judge K_final %s" % (r["defName"], r["K_ruled"], v["K_final"]))
    endorsed = {d for d, v in verdict.items() if v["verdict"] in ("accept", "adjust")}
    missing = endorsed - {r["defName"] for r in manifest}
    if missing:
        fails.append("endorsed by the judge but absent from the manifest: %s" % sorted(missing))

    descriptions = {r["defName"]: r["description"] for r in g.load(JUDGE_INPUT)}
    fails += ["reason: " + b for b in reason_findings(manifest, descriptions)]
    for name, rows in {
        "reason 'x'": [dict(manifest[0], reason="x")],
        "reason without art": [dict(manifest[0], reason=manifest[0]["reason"].split(";")[0] + "; looks scary")],
        "reason unrelated to description": [dict(manifest[0], reason="Purple zebra hums; art is a fluffy cloud")],
        "reason sharing only a function word": [dict(manifest[0], reason="These engines explode under water; "
                                                     "art shows sharp teeth")],
    }.items():
        if not reason_findings(rows, descriptions):
            fails.append("planted fault not caught: " + name)

    base = dict(manifest[0])
    plants = {
        "in-band K": dict(base, K_ruled="13", ruled_best=str(round(13 * float(base["bodySize"]), 1))),
        "wrong direction": dict(base, direction="harmless" if base["direction"] == "terror" else "terror"),
        "unknown defName": dict(base, defName="RM_NoSuchBeast"),
        "missing ruling": dict(base, ruling="my own idea"),
    }
    for name, row in plants.items():
        if not g.check([row], roster):
            fails.append("planted fault not caught: " + name)

    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "g.png")
        found = draw_and_capture(manifest, roster, out)
        if found is None:
            fails.append("graph: draw saved no figure")
        else:
            fails += found
        size = os.path.getsize(out) if os.path.exists(out) else 0
        if size < 20000:
            fails.append("graph PNG missing or tiny (%d bytes)" % size)

    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    print("PASS: %d divergences, all judge-endorsed, off-band, art+description reasons, "
          "graph regenerates with every divergence drawn and labeled; 8 planted faults caught"
          % len(manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
