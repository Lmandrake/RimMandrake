#!/usr/bin/env python3
"""TPS/FPS/heap census from JawaBench tps records (C-suite evidence, 2026-10-26).

Reads <SaveData>/JawaBench/tps/tps_*.jsonl (7-day retention) and keys EVERY reading (a `sample` row) to its scene
(TPS_SCENE_KEY_ENFORCE_LIKE_FOR_LIKE): save name, map count, map sizes and biomes, pawn count and the mod-list hash. The
sampler already records all of it - the session row's modDigest, and a `context` row every ~60 s of play (save, mapCount,
maps[] with size/biome/pawns) - so a reading takes the latest context of its own game (or, for the first window of a game,
the next one). A reading with no context has no key and compares with nothing.

Why: the 2026-10-26 BENCH bisect found the "full-list TPS drop" was a 2-map RM_PerfSite scene compared with 1-map runs
(355 vs 354 TPS like-for-like). Readings are pooled ONLY within one scene key, and --compare refuses unlike keys:

    csuite_tps.py                       per day x scene x speed: running-sample count, median TPS, ratio, FPS, max heap
    csuite_tps.py --compare A B         A, B = a session-id prefix or a day (YYYY-MM-DD); median TPS of each and the
                                        difference, or "NOT COMPARABLE: <diff>" (exit 2) when their scene keys differ

    --pawn-band PCT                     OPT-IN tolerance (default 0 = exact pawn count, the strict key): readings whose
                                        other key fields agree and whose pawn counts all lie within PCT% of the largest
                                        (ceil) are one scene, labelled pawns=lo..hi~PCT%. Why: a running colony drifts by
                                        a pawn or two (births, visitors), and exact keys split one save into a dozen rows.

Only samples with dTicks>0 (game actually ticking) count for TPS.
"""
import argparse, collections, glob, json, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_paths import LOCALLOW

D = os.environ.get("JB_TPS", os.path.join(str(LOCALLOW), "JawaBench", "tps"))

KEY_FIELDS = ("save", "mapCount", "maps", "pawns", "mods")


def cls(n):
    if n is None or n < 0:
        return "?"
    return "full" if n >= 200 else ("minimal" if n <= 60 else "mid")


def _maps(ctx):
    m = ctx.get("maps")
    return m if isinstance(m, list) else []


def scene_key(session, ctx):
    """The scene of a reading: {save, mapCount, maps, pawns, mods}, or None without a context row. maps is the sorted
    multiset of 'WxH:biome' (order of creation is not a scene difference); pawns is the spawned total over the maps the
    context lists; mods is the session's modDigest (ordinal-sorted packageIds, FNV)."""
    if ctx is None:
        return None
    maps = _maps(ctx)
    pawns = 0
    for m in maps:
        p = m.get("pawns") if isinstance(m, dict) else None
        if not isinstance(p, int) or p < 0:
            pawns = None
            break
        pawns += p
    return {
        "save": ctx.get("save") or "(new game)",
        "mapCount": ctx.get("mapCount", len(maps)),
        "maps": ",".join(sorted("%s:%s" % (m.get("size"), m.get("biome")) for m in maps if isinstance(m, dict))),
        "pawns": pawns,
        "mods": (session or {}).get("modDigest") or "?",
    }


def key_str(k):
    if k is None:
        return "(no scene)"
    return "save=%s maps=%s[%s] pawns=%s mods=%s" % (k["save"], k["mapCount"], k["maps"], k["pawns"], k["mods"])


def key_diff(a, b):
    """'' when a and b are the same scene, else the differing fields 'field: a != b; ...'. A missing key differs from
    everything, itself included (an unknown scene is never like anything)."""
    if a is None or b is None:
        return "scene: %s != %s" % (key_str(a), key_str(b))
    return "; ".join("%s: %s != %s" % (f, a[f], b[f]) for f in KEY_FIELDS if a[f] != b[f])


def comparable(a, b):
    """None when readings keyed a and b may be compared, else the refusal line 'NOT COMPARABLE: <diff>'."""
    d = key_diff(a, b)
    return None if not d else "NOT COMPARABLE: " + d


def pawn_like(lo, hi, band):
    """True when pawn counts lo..hi (lo <= hi) are one scene under a band of PCT% of the larger (ceil); band 0 = exact."""
    if lo is None or hi is None:
        return lo is None and hi is None
    return hi - lo <= -(-hi * band // 100)


def _rest(k):
    return None if k is None else tuple(k[f] for f in KEY_FIELDS if f != "pawns")


def banded(keys, band):
    """Refusal line for pooling all of keys (a list of scene keys) under a pawn band, or None when they are one scene:
    every non-pawn field equal and the whole pawn spread inside the band. band 0 is the exact key."""
    if not keys or any(k is None for k in keys):
        return comparable(keys[0] if keys else None, None)
    for k in keys[1:]:
        d = "; ".join("%s: %s != %s" % (f, keys[0][f], k[f]) for f in KEY_FIELDS if f != "pawns" and keys[0][f] != k[f])
        if d:
            return "NOT COMPARABLE: " + d
    ps = [k["pawns"] for k in keys]
    if None in ps:
        return None if all(p is None for p in ps) else "NOT COMPARABLE: pawns: %s" % sorted(ps, key=str)
    lo, hi = min(ps), max(ps)
    if not pawn_like(lo, hi, band):
        return "NOT COMPARABLE: pawns: %d != %d%s" % (lo, hi, (" (beyond the %d%% band)" % band) if band else "")
    return None


def band_label(k, lo, hi, band):
    """key_str with the pawn field shown as the band's range, so a banded row never passes for an exact one."""
    if k is None or not band:
        return key_str(k)
    return key_str(dict(k, pawns="%s..%s~%d%%" % (lo, hi, band)))


def band_rows(rs, band):
    """{id(reading): label}: readings clustered per non-pawn key, greedily over sorted distinct pawn counts (a cluster
    runs from its smallest count while pawn_like holds). band 0 labels every reading with its exact key_str."""
    if not band:
        return {id(r): key_str(r.get("scene")) for r in rs}
    by_rest = collections.defaultdict(set)
    for r in rs:
        k = r.get("scene")
        if k is not None and isinstance(k.get("pawns"), int):
            by_rest[_rest(k)].add(k["pawns"])
    span = {}
    for rest, ps in by_rest.items():
        cl = []
        for p in sorted(ps):
            if cl and pawn_like(cl[-1][0], p, band):
                cl[-1].append(p)
            else:
                cl.append([p])
        for c in cl:
            for p in c:
                span[(rest, p)] = (c[0], c[-1])
    out = {}
    for r in rs:
        k = r.get("scene")
        sp = span.get((_rest(k), k.get("pawns"))) if k is not None else None
        out[id(r)] = band_label(k, sp[0], sp[1], band) if sp else key_str(k)
    return out


def read_rows(directory):
    rows = []
    for f in sorted(glob.glob(os.path.join(directory, "tps_*.jsonl"))):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if isinstance(r, dict):
                    rows.append(r)
    return rows


def readings(rows):
    """Every sample row, with r['scene'] = its scene key (None if its game never wrote a context row) and r['mods'] =
    its session's mod count. Rows are taken per session in record order (seq); a game/menu row ends the context."""
    by_sess = collections.defaultdict(list)
    for r in rows:
        by_sess[r.get("session")].append(r)
    out = []
    for sess, rs in by_sess.items():
        rs.sort(key=lambda r: (r.get("seq") if isinstance(r.get("seq"), int) else 0))
        session = next((r for r in rs if r.get("kind") == "session"), None)
        ctx, pending = None, []
        for r in rs:
            k = r.get("kind")
            if k in ("game", "menu"):
                for p in pending:
                    p["scene"] = None
                ctx, pending = None, []
            elif k == "context":
                ctx = r
                for p in pending:
                    p["scene"] = scene_key(session, ctx)
                pending = []
            elif k == "sample":
                r = dict(r)
                r["mods"] = (session or {}).get("mods")
                if ctx is None:
                    pending.append(r)
                else:
                    r["scene"] = scene_key(session, ctx)
                out.append(r)
        for p in pending:
            p["scene"] = None
    return out


def running(rs):
    return [r for r in rs if (r.get("dTicks") or 0) > 0 and r.get("tps")]


def select(rs, sel):
    return [r for r in rs if str(r.get("session") or "").startswith(sel) or str(r.get("utc") or "")[:10] == sel]


def compare(rs, a, b, out=print, band=0):
    """Median TPS of selection a vs b, or NOT COMPARABLE. Each side must itself be one scene (pooling two scenes into a
    median is the same mistake). Returns the process exit code: 0 compared, 2 refused, 1 nothing to compare. band > 0
    (--pawn-band) lets pawn counts differ within PCT% across both sides together; the scene line then shows the range."""
    sides = []
    for sel in (a, b):
        run = running(select(rs, sel))
        if not run:
            out("NO READINGS: %s has no running samples" % sel)
            return 1
        keys = {}
        for r in run:
            keys.setdefault(key_str(r.get("scene")), r.get("scene"))
        ks = list(keys.values())
        if band:
            refusal = banded(ks, band)
            if refusal:
                out("NOT COMPARABLE: %s spans %d scenes (%s)" % (sel, len(keys), refusal[len("NOT COMPARABLE: "):]))
                return 2
        elif len(keys) != 1 or None in keys.values():
            diff = key_diff(ks[0], ks[1]) if len(ks) > 1 else key_diff(ks[0], ks[0])
            out("NOT COMPARABLE: %s spans %d scenes (%s)" % (sel, len(keys), diff))
            return 2
        sides.append((sel, ks, run))
    allk = sides[0][1] + sides[1][1]
    refusal = banded(allk, band) if band else comparable(sides[0][1][0], sides[1][1][0])
    if refusal:
        out(refusal)
        return 2
    ma, mb = (st.median([r["tps"] for r in s[2]]) for s in sides)
    ps = [k["pawns"] for k in allk]
    out("scene: %s" % (band_label(allk[0], min(ps), max(ps), band) if band and None not in ps else key_str(allk[0])))
    out("%s: n=%d medTPS=%.1f | %s: n=%d medTPS=%.1f | delta=%+.1f (%+.1f%%)"
        % (a, len(sides[0][2]), ma, b, len(sides[1][2]), mb, mb - ma, (mb - ma) * 100.0 / ma if ma else float("nan")))
    return 0


def census(rs, out=print, band=0):
    groups = collections.defaultdict(list)
    sess_seen = collections.defaultdict(set)
    label = band_rows(rs, band)
    for r in rs:
        day = str(r.get("utc") or "")[:10]
        ks = label[id(r)]
        sess_seen[(day, ks)].add(r.get("session"))
        groups[(day, ks, r.get("mult"))].append(r)
    out("day        class    mult  n_run  medTPS  medRatio  medFPS(all)  maxHeapMB  sessions  scene")
    for (day, ks, m), g in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], str(x[0][2]))):
        run = running(g)
        fps = [r["fps"] for r in g if r.get("fps") is not None]
        heap = [r["heapMB"] for r in g if r.get("heapMB") is not None]
        rat = [r["ratio"] for r in run if r.get("ratio") is not None]
        if not run and m not in (0, None):
            continue
        out(f"{day} {cls(g[0].get('mods')):8} {str(m):5} {len(run):6} "
            f"{(st.median([r['tps'] for r in run]) if run else float('nan')):7.1f} "
            f"{(st.median(rat) if rat else float('nan')):8.2f} "
            f"{(st.median(fps) if fps else float('nan')):11.1f} "
            f"{(max(heap) if heap else float('nan')):9.0f}  {len(sess_seen[(day, ks)]):8}  {ks}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=D, help="the JawaBench tps record directory (env JB_TPS)")
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"), help="session-id prefix or YYYY-MM-DD for each side")
    ap.add_argument("--pawn-band", type=int, default=0, metavar="PCT",
                    help="pawn counts within PCT%% of the larger are one scene (default 0: exact); labelled pawns=lo..hi~PCT%%")
    a = ap.parse_args(argv)
    if not 0 <= a.pawn_band < 100:
        ap.error("--pawn-band must be 0..99")
    rs = readings(read_rows(a.dir))
    if a.compare:
        return compare(rs, a.compare[0], a.compare[1], band=a.pawn_band)
    census(rs, band=a.pawn_band)
    return 0


if __name__ == "__main__":
    sys.exit(main())
