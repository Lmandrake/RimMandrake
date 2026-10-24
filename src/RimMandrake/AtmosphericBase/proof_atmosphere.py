#!/usr/bin/env python3
"""proof_atmosphere.py -- the time-aware proof of AtmosphericBase (laws L4-L13, the gentle default, cost, hygiene).

Plan, bands and the hook contract: design/RimMandrake/atmospheric_base_proof_plan_2026-10-23.md. In short:

  * V clock (virtual): the proof hook RM_AtmosphericBaseProof.ProofSample steps the SHIPPED RM_Compositor.Evaluate(comp, t)
    at t0 + k*dt and hands every sample back. Deterministic, instant, repeatable; three seeds, all must pass.
  * R clock (real): only L10 -- the game is paused (proven by a ticksGame delta of 0) and Showing(Thing) is sampled on the
    wall clock for one mass period; two runs, both must pass.
  * G (game ticks / Scribe): only R1, the save-and-reload row (opt-in, --with-reload).

The script also runs the mod's own self-judging hooks (ProofTakeover / ProofCompositor / ProofTerritory) as K rows, and
cross-checks them against the independent V measurements (X1).

Statuses: PASS, FAIL, UNMEASURED (never PASS: could not ask, too few fixtures, hook not built). Classes: MOD (the mod is
wrong), SITE (the map cannot show it), HARNESS (the instrument could not ask or could not see).

Modes:
  --selftest       stub bridge only; runs the good model and every bad model and asserts each flips its own row. No game.
  --offline        disk-only rows (P1, D1): the hook source and the shipped defaults.
  (default)        live, through the bridge. Run from the repo root under python.exe, piped through `tr -d '\\r'`.
Results go to D:\\ClaudeWork\\rimmandrake\\scratch\\proof_atmosphere\\ (override with --out).
"""
import argparse
import json
import math
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
PROOF_TYPE = "RimMandrake.AtmosphericBase.RM_AtmosphericBaseProof"
PACKAGE_ID = "mandrake.rm.atmosphericbase"
DEFAULT_OUT = "/mnt/d/ClaudeWork/rimmandrake/scratch/proof_atmosphere"

PASS, FAIL, UNM, INF = "PASS", "FAIL", "UNMEASURED", "INFERRED"
MOD, SITE, HARNESS = "MOD", "SITE", "HARNESS"

# ---------------------------------------------------------------- the law constants (RM_TerritoryKernel / RM_TremorKernel /
# RM_SchemeKernel). Bands are derived from THESE, never from what the code happens to output today.
MIN_PERIOD = 240.0          # L5: the front is slow; a shorter setting is clamped
MIN_LEAD, MAX_LEAD = 0.5, 0.8
MAX_RAGGED = 0.25
STEPS_PER_TURN = 240
LAW_CAP = 3                 # L6: at most three tremor contributors
MAX_FRACTION = 0.10         # L6: never more than a tenth of the lights flicker at once
MAX_FLICKER = 2.0
WHITE_FLOOR = 200           # L11: every channel >= 200 reads as Narrator white
MIN_LIT, MIN_SPREAD = 10, 8  # a territory needs this many lit fixtures over this many distinct cells to show a front
LIGHT_SHOW_PER_MIN = 6      # gentle default: a fixture changes at most this often per minute...
LIGHT_SHOW_MIN_GAP = 2.0    # ...and never twice within this many seconds
COST_MS_PER_100 = 0.1       # PROVISIONAL budget: ms per Evaluate per 100 fixtures

# the keys the mod's own hooks must answer True (copied from validation.py's _want lists, 2026-10-23)
K_WANT = {
    "ProofTakeover": ("bound", "buttons_registered", "offered", "take", "release_offered", "drive", "released", "restored",
                      "drive_after_release_refused", "neighbour", "channel_off", "channel_off_releases", "button_off_hides"),
    "ProofCompositor": ("push", "first_write", "quantised", "changed_only", "neighbour", "outside_group_substrate",
                        "compositor_off_substrate", "compositor_on_drives", "mood_release_substrate", "default_runs",
                        "released_exact"),
    "ProofTerritory": ("one_owner", "own_palette", "territory_off_one_mood", "both_sides", "boundary_moves",
                       "tremor_cap_held", "tremor_fraction_held", "tremor_own_palette", "released_exact"),
}


# ---------------------------------------------------------------- pure kernel mirrors
def lead_count(n, share):
    """RM_TerritoryKernel.LeadCount: ceil(n * clamp(share)), and with two or more fixtures both claimants hold ground."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    k = int(math.ceil(n * min(MAX_LEAD, max(MIN_LEAD, share)) - 1e-9))
    return max(1, min(n - 1, k))


def clock_step(t, period):
    return int(math.floor(t / max(MIN_PERIOD, period) * STEPS_PER_TURN))


def law_instant_ceiling(n):
    """The L6 ceiling on fixtures flickering at one instant, whatever the setting says: max(1, floor(n * 0.10))."""
    return max(1, int(math.floor(n * MAX_FRACTION + 1e-4)))


def seeds(period):
    """Three start times: round, off-phase, and a day of uptime (realtimeSinceStartup is a float32)."""
    return [1000.0, 1000.0 + 0.37 * period, 86400.5]


def _rgb(fx):
    return (int(fx[1]), int(fx[2]), int(fx[3]))


def _is_white(c):
    return all(int(x) >= WHITE_FLOOR for x in c[:3])


def _pal(p):
    return set(tuple(int(v) for v in x[:3]) for x in (p or []))


def _span(samples):
    return (samples[-1]["t"] - samples[0]["t"]) if len(samples) >= 2 else 0.0


def _dt(samples):
    return max((b["t"] - a["t"]) for a, b in zip(samples, samples[1:])) if len(samples) >= 2 else float("inf")


def _r(status, cls, detail):
    return (status, cls, detail)


# ---------------------------------------------------------------- pure metrics: each takes series results and returns
# (status, class, detail). A series result is the hook's answer for one scenario and seed (see the plan's contract).
def m_palette(results, allowed):
    off, seen = [], 0
    for R in results:
        for s in R["samples"]:
            for fx in s["fx"]:
                if fx[5] in ("S", "N"):
                    continue                 # substrate is the vanilla colour; the Narrator's white is L11's business
                seen += 1
                if _rgb(fx) not in allowed:
                    off.append((round(s["t"], 2), fx[0], _rgb(fx)))
    if seen == 0:
        return _r(UNM, HARNESS, "no driven colour sampled")
    if off:
        return _r(FAIL, MOD, "%d of %d driven samples off every declared palette, e.g. %s" % (len(off), seen, off[:3]))
    return _r(PASS, MOD, "%d driven samples, all on a declared palette" % seen)


def m_writes(R):
    s = R["samples"]
    if len(s) < 2 or any("writes" not in x for x in s):
        return _r(UNM, HARNESS, "series carries no per-evaluation write count")
    bad = []
    for a, b in zip(s, s[1:]):
        pa = dict((fx[0], _rgb(fx)) for fx in a["fx"])
        changed = sum(1 for fx in b["fx"] if fx[5] != "S" and pa.get(fx[0]) != _rgb(fx))
        if changed != int(b["writes"]):
            bad.append((round(b["t"], 2), changed, b["writes"]))
    same = R.get("same_t_writes")
    if same is None:
        return _r(UNM, HARNESS, "hook did not re-evaluate at the same t (same_t_writes missing)")
    if bad or int(same) != 0:
        return _r(FAIL, MOD, "writes != changed emitters at %d steps %s; same-t re-evaluation wrote %s" % (len(bad), bad[:3], same))
    return _r(PASS, MOD, "writes equal the changed emitters at all %d steps; same-t re-evaluation wrote 0" % (len(s) - 1))


def m_lead(R):
    n = len(R["samples"][0]["fx"]) if R["samples"] else 0
    want = lead_count(n, float(R.get("lead_share", 0.6)))
    bad = []
    for s in R["samples"]:
        lead = sum(1 for fx in s["fx"] if fx[4] == 0)
        other = sum(1 for fx in s["fx"] if fx[4] == 1)
        if lead != want or other < 1 or lead + other != n:
            bad.append((round(s["t"], 2), lead, other))
    if n < 2:
        return _r(UNM, SITE, "fewer than two fixtures in the union")
    if bad:
        return _r(FAIL, MOD, "leader held != LeadCount(%d, %.2f)=%d or a side empty at %d samples, e.g. %s" % (
            n, float(R.get("lead_share", 0.6)), want, len(bad), bad[:3]))
    return _r(PASS, MOD, "leader holds exactly %d of %d at every sample, the other side at least 1" % (want, n))


def m_mixing(R):
    lead, other = _pal(R["palettes"]["lead"]), _pal(R["palettes"]["other"])
    bad, seen = [], 0
    for s in R["samples"]:
        for fx in s["fx"]:
            if fx[5] not in ("L", "O"):
                continue
            seen += 1
            if _rgb(fx) not in (lead if fx[4] == 0 else other):
                bad.append((round(s["t"], 2), fx[0], fx[4], _rgb(fx)))
    if seen == 0:
        return _r(UNM, HARNESS, "no territory sample")
    if bad:
        return _r(FAIL, MOD, "%d of %d territory samples not in their owner's palette (mixing), e.g. %s" % (len(bad), seen, bad[:3]))
    return _r(PASS, MOD, "%d territory samples, each in its owner's own palette" % seen)


def m_boundary(R):
    s, P = R["samples"], max(MIN_PERIOD, float(R["period"]))
    if _span(s) < P - 1e-6:
        return _r(UNM, HARNESS, "series spans %.0f s, shorter than one turn (%.0f s)" % (_span(s), P))
    first = dict((fx[0], fx[4]) for fx in s[0]["fx"])
    moved = set(fx[0] for x in s for fx in x["fx"] if fx[4] != first.get(fx[0]))
    n, share = len(first), float(R.get("lead_share", 0.6))
    bar = 1.0 - min(MAX_LEAD, max(MIN_LEAD, share))
    frac = len(moved) / float(n) if n else 0.0
    if frac + 1e-9 < bar:
        return _r(FAIL, MOD, "only %d/%d fixtures changed owner in one turn (%.2f < bar %.2f): the boundary is static" % (len(moved), n, frac, bar))
    return _r(PASS, MOD, "%d/%d fixtures changed owner in one turn (bar >= %.2f)" % (len(moved), n, bar))


def m_front_clock(R, requested_short=None):
    """Owner changes only where ClockStep(t, max(240, period)) changes; the effective period is never under 240 s."""
    s, P = R["samples"], float(R["period"])
    if requested_short is not None:
        if P + 1e-6 < MIN_PERIOD:
            return _r(FAIL, MOD, "a %.0f s setting ran at period %.0f s (< %.0f): not clamped" % (requested_short, P, MIN_PERIOD))
        return _r(PASS, MOD, "a %.0f s setting ran at %.0f s (clamped)" % (requested_short, P))
    if P + 1e-6 < MIN_PERIOD:
        return _r(FAIL, MOD, "effective period %.0f s < %.0f" % (P, MIN_PERIOD))
    bad = []
    for a, b in zip(s, s[1:]):
        oa = dict((fx[0], fx[4]) for fx in a["fx"])
        flips = [fx[0] for fx in b["fx"] if oa.get(fx[0]) != fx[4]]
        if flips and clock_step(a["t"], P) == clock_step(b["t"], P):
            bad.append((round(b["t"], 2), flips[:3]))
        if "step" in b and int(b["step"]) != clock_step(b["t"], P):
            bad.append((round(b["t"], 2), "step %s != %d" % (b["step"], clock_step(b["t"], P))))
    if bad:
        return _r(FAIL, MOD, "owner changed off the front's clock at %d samples, e.g. %s" % (len(bad), bad[:3]))
    return _r(PASS, MOD, "every owner change falls on a ClockStep boundary (period %.0f s)" % P)


def m_rank_swap(R1, R2):
    a, b = R1.get("lead_claimant"), R2.get("lead_claimant")
    if not a or not b:
        return _r(UNM, HARNESS, "series does not name the lead claimant")
    if a == b:
        return _r(FAIL, MOD, "swapping the ranks left %s leading" % a)
    return _r(PASS, MOD, "swapping the ranks swapped the leader (%s -> %s)" % (a, b))


def m_tremor(R, flicker):
    """L6 a/b/c as three verdicts: contributors <= 3; at most the law ceiling at one instant; flicker in its own palette."""
    s = R["samples"]
    need_dt = min(0.4, float(flicker) / 2.0)
    if _dt(s) > need_dt + 1e-6 or _span(s) < 240.0 - 1e-6:
        u = _r(UNM, HARNESS, "sampling too coarse or short for flickers (dt %.2f > %.2f or span %.0f < 240 s)" % (_dt(s), need_dt, _span(s)))
        return u, u, u
    tpal = [_pal(p) for p in R["palettes"].get("tremor") or []]
    n = len(s[0]["fx"])
    ceil_n = law_instant_ceiling(n)
    maxc = max(int(x.get("contributors", 0)) for x in s)
    tmax, seen, wrong = 0, 0, []
    for x in s:
        t = [fx for fx in x["fx"] if fx[5] == "T"]
        tmax = max(tmax, len(t))
        seen += len(t)
        for fx in t:
            c = int(fx[6]) if len(fx) > 6 else -1
            if c < 0 or c >= len(tpal) or _rgb(fx) not in tpal[c]:
                wrong.append((round(x["t"], 2), fx[0], c, _rgb(fx)))
    if seen == 0:
        u = _r(UNM, SITE, "no flicker in %.0f s: nothing to judge" % _span(s))
        return u, u, u
    a = _r(FAIL, MOD, "%d tremor contributors (> %d)" % (maxc, LAW_CAP)) if maxc > LAW_CAP else \
        _r(PASS, MOD, "at most %d contributors (cap %d)" % (maxc, LAW_CAP))
    b = _r(FAIL, MOD, "%d of %d fixtures flickered at once (> law ceiling %d): tremor reads as territory" % (tmax, n, ceil_n)) \
        if tmax > ceil_n else _r(PASS, MOD, "at most %d of %d at once (ceiling %d); %d flicker-samples" % (tmax, n, ceil_n, seen))
    c = _r(FAIL, MOD, "%d flickers not in their contributor's palette, e.g. %s" % (len(wrong), wrong[:3])) if wrong else \
        _r(PASS, MOD, "all %d flicker-samples in their contributor's own palette" % seen)
    return a, b, c


def m_dark(R, mass):
    """L8: in a scheme that may go dark, every window of one mass period has a lit frame and some variance."""
    s = R["samples"]
    if _span(s) < mass - 1e-6:
        return _r(UNM, HARNESS, "series shorter than one mass period")
    bad = []
    ids = [fx[0] for fx in s[0]["fx"]]
    for i in ids:
        ser = [(x["t"], next(_rgb(fx) for fx in x["fx"] if fx[0] == i)) for x in s]
        t = ser[0][0]
        while t + mass <= ser[-1][0] + 1e-6:
            w = [c for (tt, c) in ser if t - 1e-9 <= tt <= t + mass + 1e-9]
            if all(max(c) == 0 for c in w) or len(set(w)) < 2:
                bad.append((i, round(t, 1)))
                break
            t += mass / 2.0
    if bad:
        return _r(FAIL, MOD, "%d fixtures still or black for a whole mass period, e.g. %s" % (len(bad), bad[:3]))
    return _r(PASS, MOD, "every fixture moves and lights in every %.0f s window" % mass)


def m_white(results):
    bad = []
    for R in results:
        for s in R["samples"]:
            for fx in s["fx"]:
                if fx[5] not in ("N", "S") and _is_white(_rgb(fx)):
                    bad.append((R.get("scenario"), round(s["t"], 2), fx[0], _rgb(fx)))
    if bad:
        return _r(FAIL, MOD, "%d non-Narrator samples read white, e.g. %s" % (len(bad), bad[:3]))
    return _r(PASS, MOD, "no non-Narrator sample has every channel >= %d" % WHITE_FLOOR)


def m_light_show(R):
    s = R["samples"]
    if _span(s) < 60.0 or _dt(s) > LIGHT_SHOW_MIN_GAP / 2.0 + 1e-6:
        return _r(UNM, HARNESS, "need >= 60 s at dt <= 1 s to judge a light show")
    worst_rate, worst_gap = 0.0, float("inf")
    for i in [fx[0] for fx in s[0]["fx"]]:
        ts, prev = [], None
        for x in s:
            c = next(_rgb(fx) for fx in x["fx"] if fx[0] == i)
            if prev is not None and c != prev:
                ts.append(x["t"])
            prev = c
        worst_rate = max(worst_rate, len(ts) / (_span(s) / 60.0))
        worst_gap = min([worst_gap] + [b - a for a, b in zip(ts, ts[1:])])
    if worst_rate > LIGHT_SHOW_PER_MIN + 1e-9 or worst_gap < LIGHT_SHOW_MIN_GAP - 1e-9:
        return _r(FAIL, MOD, "light show: a fixture changes %.1f/min (bar %d) or twice within %.2f s (bar %.0f)" % (
            worst_rate, LIGHT_SHOW_PER_MIN, worst_gap, LIGHT_SHOW_MIN_GAP))
    return _r(PASS, MOD, "gentle: at most %.1f changes/min per fixture, shortest gap %s s" % (
        worst_rate, "-" if worst_gap == float("inf") else "%.1f" % worst_gap))


def m_restore(R):
    """L13: after t_g + D every fixture equals the COUNTERFACTUAL twin (the substrate evaluated at the same t)."""
    end = float(R["t_g"]) + float(R["D"])
    after = [(x, tw) for x, tw in zip(R["samples"], R["twin"]) if x["t"] >= end - 1e-9]
    if not after:
        return _r(UNM, HARNESS, "no sample after the gesture ended")
    bad = []
    for x, tw in after:
        want = dict((fx[0], _rgb(fx)) for fx in tw)
        for fx in x["fx"]:
            if want.get(fx[0]) != _rgb(fx):
                bad.append((round(x["t"], 2), fx[0], _rgb(fx), want.get(fx[0])))
    if bad:
        return _r(FAIL, MOD, "%d fixture-samples differ from the no-gesture twin after the gesture, e.g. %s" % (len(bad), bad[:3]))
    return _r(PASS, MOD, "%d samples after the gesture equal the no-gesture twin exactly" % len(after))


def m_envelope(R):
    """Narrator: rises to white, then dims (non-increasing within the palette's own spread) for longer than the rise."""
    tg, D = float(R["t_g"]), float(R["D"])
    inside = [x for x in R["samples"] if tg - 1e-9 <= x["t"] < tg + D]
    if len(inside) < 4:
        return _r(UNM, HARNESS, "fewer than 4 samples inside the gesture")
    lum = [sum(sum(_rgb(fx)) for fx in x["fx"]) / (3.0 * max(1, len(x["fx"]))) for x in inside]
    k = max(range(len(lum)), key=lambda i: lum[i])
    peak_white = all(_is_white(_rgb(fx)) for fx in inside[k]["fx"])
    pal = [sum(c) / 3.0 for c in _pal(R["palettes"].get("lead"))] or [0.0]
    tol = max(pal) - min(pal)
    rises = [(round(inside[i]["t"], 2), round(lum[i] - lum[i - 1], 1)) for i in range(k + 1, len(lum)) if lum[i] > lum[i - 1] + tol + 1e-9]
    rise_t, dim_t = inside[k]["t"] - tg, tg + D - inside[k]["t"]
    if not peak_white or rises or dim_t <= rise_t:
        return _r(FAIL, MOD, "envelope: peak white=%s, dim rises %s, rise %.2f s vs dim %.2f s" % (peak_white, rises[:3], rise_t, dim_t))
    return _r(PASS, MOD, "rises to white in %.2f s, dims for %.2f s without brightening" % (rise_t, dim_t))


def m_narrator_wins(R):
    tg, D = float(R["t_g"]), float(R["D"])
    inside = [x for x in R["samples"] if tg - 1e-9 <= x["t"] < tg + D]
    if not inside:
        return _r(UNM, HARNESS, "no sample inside the gesture")
    lost = [(round(x["t"], 2), fx[0], fx[5]) for x in inside for fx in x["fx"] if fx[5] != "N"]
    if lost:
        return _r(FAIL, MOD, "the alarm held %d fixture-samples during the Narrator's gesture, e.g. %s" % (len(lost), lost[:3]))
    return _r(PASS, MOD, "the Narrator held every fixture through %d samples against the alarm" % len(inside))


def m_control_static(results):
    vals = set()
    n = 0
    for R in results:
        for s in R["samples"]:
            if s.get("ctl") is not None:
                vals.add(tuple(s["ctl"][:3]))
                n += 1
    if n == 0:
        return _r(UNM, HARNESS, "no untaken control fixture in the series")
    if len(vals) > 1:
        return _r(FAIL, MOD, "an untaken fixture changed colour (%d values): the mod touched a light it does not hold" % len(vals))
    return _r(PASS, HARNESS, "untaken control fixture static over %d samples: the sampler invents no motion" % n)


def m_l10(runs, control_values):
    """runs: [{"ticks_moved": int, "values": [...]}]. Each run must hold the pause and see >= 1 transition."""
    if any(r["ticks_moved"] != 0 for r in runs):
        return _r(UNM, HARNESS, "the pause did not hold (ticksGame moved by %s): cannot separate real time from game time" % [r["ticks_moved"] for r in runs])
    if any(v is not None for v in control_values):
        return _r(FAIL, MOD, "an untaken control fixture reported a scheme: %s" % [v for v in control_values if v][:2])
    trans = [sum(1 for a, b in zip(r["values"], r["values"][1:]) if a != b) for r in runs]
    if any(v in (None, "") for r in runs for v in r["values"]):
        return _r(FAIL, MOD, "a held fixture showed nothing while paused: %s" % [r["values"][:4] for r in runs])
    if any(t < 1 for t in trans):
        return _r(FAIL, MOD, "paused, the held fixture did not change in a whole mass period (transitions per run %s)" % trans)
    return _r(PASS, MOD, "paused (0 ticks), the held fixture changed %s times per run; the untaken control stayed null" % trans)


# ---------------------------------------------------------------- offline readers (P1, D1)
def read_defaults(settings_cs, schemes_xml, compositor_cs):
    """The shipped defaults, read from source: settings field initialisers, the default scheme's def, every palette."""
    out = {}
    for typ, name, val in re.findall(r"public\s+(bool|int|float)\s+(\w+)\s*=\s*([^;]+);", settings_cs):
        v = val.strip().rstrip("fF")
        out[name] = (v == "true") if typ == "bool" else (int(v) if typ == "int" else float(v))
    m = re.search(r'DefaultSchemeDefName\s*=\s*"(\w+)"', compositor_cs)
    out["defaultScheme"] = m.group(1) if m else None
    schemes = {}
    root = ET.fromstring(schemes_xml)
    for d in root:
        dn = d.findtext("defName")
        if not dn:
            continue
        pal = []
        for li in d.findall("palette/li"):
            nums = [int(float(x)) for x in re.findall(r"[\d.]+", li.text or "")]
            pal.append(tuple(nums[:3]))
        schemes[dn] = {"palette": pal, "mayGoDark": (d.findtext("mayGoDark") or "false").strip().lower() == "true",
                       "flasherCount": int(d.findtext("flasherCount") or 0),
                       "massPeriodSeconds": float(d.findtext("massPeriodSeconds") or 120)}
    out["schemes"] = schemes
    return out


def judge_defaults(d):
    bad = []
    sch = (d.get("schemes") or {}).get(d.get("defaultScheme") or "")
    if sch is None:
        return _r(UNM, HARNESS, "default scheme %r not found among the shipped defs" % d.get("defaultScheme"))
    if sch["flasherCount"] != 0:
        bad.append("default flasherCount %d" % sch["flasherCount"])
    if sch["mayGoDark"]:
        bad.append("default mayGoDark")
    for dn, s in sorted(d["schemes"].items()):
        w = [c for c in s["palette"] if _is_white(c)]
        if w:
            bad.append("%s palette has white %s" % (dn, w))
        if len(s["palette"]) > 8:
            bad.append("%s palette > 8" % dn)
    chk = (("territoryPeriodSeconds", lambda v: v >= MIN_PERIOD), ("territoryLeadShare", lambda v: MIN_LEAD <= v <= MAX_LEAD),
           ("territoryRagged", lambda v: 0 <= v <= MAX_RAGGED), ("tremorCap", lambda v: v <= LAW_CAP),
           ("tremorMaxFraction", lambda v: v <= MAX_FRACTION), ("tremorFlickerSeconds", lambda v: v <= MAX_FLICKER))
    for k, ok in chk:
        if k not in d:
            bad.append("%s not readable" % k)
        elif not ok(d[k]):
            bad.append("%s=%s" % (k, d[k]))
    if bad:
        return _r(FAIL, MOD, "the shipped default is not gentle: %s" % "; ".join(bad))
    return _r(PASS, MOD, "default %s: flashers 0, never dark, no white anywhere, period %.0f s, tremor cap %d / fraction %.2f" % (
        d["defaultScheme"], d["territoryPeriodSeconds"], int(d["tremorCap"]), d["tremorMaxFraction"]))


def offline_rows(rows):
    src = os.path.join(HERE, "Source")
    proof_cs = open(os.path.join(src, "RM_AtmosphericBaseProof.cs"), encoding="utf-8").read()
    has = re.search(r"public static string ProofSample\(string \w+\)", proof_cs) is not None
    add(rows, "P1.hook_in_source", PASS if has else UNM, HARNESS,
        "ProofSample declared in RM_AtmosphericBaseProof.cs" if has else "ProofSample not in source yet: every V row will read UNMEASURED")
    d = read_defaults(open(os.path.join(src, "RM_AtmosphericBaseSettings.cs"), encoding="utf-8").read(),
                      open(os.path.join(HERE, "Defs", "RM_AtmosphericSchemes.xml"), encoding="utf-8").read(),
                      open(os.path.join(src, "RM_AtmosphericCompositor.cs"), encoding="utf-8").read())
    add(rows, "D1.default_gentle_disk", *judge_defaults(d))
    return d


# ---------------------------------------------------------------- rows
def add(rows, rid, status, cls, detail):
    rows.append({"id": rid, "status": status, "class": cls, "detail": detail})
    print("%-30s %-10s %-7s %s" % (rid, status, cls, str(detail)[:150]), flush=True)


V_ROWS = ("S2.control_static", "S3.deterministic", "L4.quantised", "W1.changed_only", "L5a.lead_count", "L5b.no_mixing",
          "L5c.boundary_moves", "L5d.front_clock", "L5d.period_clamped", "L5e.rank_order", "L6a.tremor_cap",
          "L6b.tremor_fraction", "L6c.tremor_own_palette", "L8.dark_never_still", "L9.unlit_untouched", "L11a.never_white",
          "L11b.white_scheme_rejected", "L12.narrator_outranks_alarm", "L13.gesture_restores", "N1.narrator_envelope",
          "D2.default_gentle_live", "D3.no_light_show", "C1.cost", "X1.k_and_v_agree", "R2.left_as_found")


def proof(I, rows, with_reload=False, disk_defaults=None):
    """The whole run against an instrument I (live bridge or stub). Never raises past a row."""
    up = I.alive()
    add(rows, "P2.bridge_and_tier", PASS if up.get("ok") else UNM, HARNESS, up.get("detail"))
    if not up.get("ok"):
        return
    lg = I.log_revive()
    add(rows, "P3.log_alive", PASS if lg.get("alive") else UNM, HARNESS, "log sentinel round-trip %s" % ("seen" if lg.get("alive") else "NOT seen"))

    # K rows: the mod's own self-judging hooks
    kv_all = {}
    for meth, want in sorted(K_WANT.items()):
        kv, why = I.legacy(meth)
        if kv is None:
            add(rows, "K.%s" % meth, UNM, HARNESS, why)
            continue
        kv_all[meth] = kv
        if kv.get("map") == "-" or kv.get("lit") == "-":
            add(rows, "K.%s" % meth, UNM, SITE, "no map or no lit fixture: %s" % kv)
            continue
        absent = [k for k in want if k not in kv]
        false = dict((k, kv[k]) for k in want if k in kv and kv[k] != "True")
        if false:
            add(rows, "K.%s" % meth, FAIL, MOD, "hook answered %s" % false)
        elif absent:
            add(rows, "K.%s" % meth, UNM, HARNESS, "hook did not answer %s (fewer fixtures, or older DLL)" % absent)
        else:
            add(rows, "K.%s" % meth, PASS, MOD, "%d keys True" % len(want))

    # V rows gate: the hook must exist, the site must show a front, the sampler must see
    pick, why = I.hook("pick")
    gate = None
    if pick is None:
        gate = (UNM, HARNESS, "ProofSample hook not built or not deployed: %s" % why)
    elif int(pick.get("lit", 0)) < MIN_LIT or int(pick.get("spread", 0)) < MIN_SPREAD:
        gate = (UNM, SITE, "only %s lit fixtures over %s cells (need %d over %d)" % (pick.get("lit"), pick.get("spread"), MIN_LIT, MIN_SPREAD))
    if gate is None:
        snap0, _ = I.hook("snapshot")
        san, why = I.hook("sanity")
        if san is None:
            gate = (UNM, HARNESS, "sanity probe unanswered: %s" % why)
        else:
            a, b = tuple(san["a"][:3]), tuple(san["b"][:3])
            f0, f1 = tuple(san["forced"][0][:3]), tuple(san["forced"][1][:3])
            ok = a == f0 and b == f1 and a != b
            add(rows, "S1.sampler_sees", PASS if ok else FAIL, HARNESS,
                "forced %s then %s, read %s then %s" % (f0, f1, a, b))
            if not ok:
                gate = (UNM, HARNESS, "the sampler cannot see a forced colour change (S1)")
    if gate is not None:
        for rid in V_ROWS:
            add(rows, rid, *gate)
        l10(I, rows, None, None)
        reload_row(I, rows, None, with_reload)
        log_row(I, rows)
        return
    try:
        v_rows(I, rows, pick, kv_all, disk_defaults)
    finally:
        snap1, _ = I.hook("snapshot")
        same = snap0 is not None and snap1 is not None and snap0.get("fx") == snap1.get("fx")
        if snap0 is None or snap1 is None:
            add(rows, "R2.left_as_found", UNM, HARNESS, "snapshot probe unanswered before or after the run")
        else:
            add(rows, "R2.left_as_found", PASS if same else FAIL, MOD,
                "every fixture as before the run" if same else "fixtures differ from the before-snapshot")
    l10(I, rows, pick, (I.settings or {}).get("default_scheme"))
    reload_row(I, rows, pick, with_reload)
    log_row(I, rows)


def _series(I, scenario, t0, dt, n, **kw):
    R, why = I.hook("series", scenario=scenario, t0=t0, dt=dt, n=n, **kw)
    if R is None:
        return None, _r(UNM, HARNESS, "scenario %s: %s" % (scenario, why))
    if R.get("unknown_scenario") or R.get("not_built"):
        return None, _r(UNM, HARNESS, "scenario %s not built in the hook yet" % scenario)
    if R.get("unsupported"):
        return None, _r(UNM, MOD, "scenario %s: %s" % (scenario, R["unsupported"]))
    if not R.get("samples"):
        return None, _r(UNM, SITE, "scenario %s returned no samples" % scenario)
    R["scenario"] = scenario
    return R, None


def _worst(verdicts):
    """All seeds must pass: FAIL beats UNMEASURED beats PASS; the detail names the seed."""
    order = {FAIL: 0, UNM: 1, INF: 2, PASS: 3}
    k = min(range(len(verdicts)), key=lambda i: order[verdicts[i][1][0]])
    seed, (st, cl, de) = verdicts[k]
    return st, cl, ("seed t0=%s: %s" % (seed, de)) if st != PASS else ("all %d seeds: %s" % (len(verdicts), de))


def v_rows(I, rows, pick, kv_all, disk_defaults):
    st, why_settings = I.hook("settings")
    I.settings = st or {}
    cur = (st or {}).get("settings") or {}
    P = max(MIN_PERIOD, float(cur.get("territoryPeriodSeconds", 900.0)))
    flick = float(cur.get("tremorFlickerSeconds", 0.8))
    c0, _ = I.hook("counters")

    terr, allR, verd = [], [], {}
    for t0 in seeds(P):
        R, u = _series(I, "territory", t0, P / STEPS_PER_TURN, STEPS_PER_TURN + 1)
        for rid, f in (("W1.changed_only", m_writes), ("L5a.lead_count", m_lead), ("L5b.no_mixing", m_mixing),
                       ("L5c.boundary_moves", m_boundary), ("L5d.front_clock", m_front_clock)):
            verd.setdefault(rid, []).append((t0, u if R is None else f(R)))
        if R is not None:
            terr.append(R)
    R2, _ = _series(I, "territory", seeds(P)[0], P / STEPS_PER_TURN, STEPS_PER_TURN + 1)
    if not terr or R2 is None:
        add(rows, "S3.deterministic", UNM, HARNESS, "territory series unavailable")
    else:
        same = json.dumps(terr[0]["samples"], sort_keys=True) == json.dumps(R2["samples"], sort_keys=True)
        add(rows, "S3.deterministic", PASS if same else FAIL, MOD if not same else HARNESS,
            "the same t0 twice gives byte-identical samples" if same else "the same t0 twice gave different samples: Evaluate is not a pure function of t")
    tremV = {}
    for t0 in seeds(P):
        R, u = _series(I, "tremor", t0, min(0.4, flick / 2.0), int(math.ceil(240.0 / min(0.4, flick / 2.0))) + 1)
        abc = (u, u, u) if R is None else m_tremor(R, flick)
        for rid, v in zip(("L6a.tremor_cap", "L6b.tremor_fraction", "L6c.tremor_own_palette"), abc):
            tremV.setdefault(rid, []).append((t0, v))
        if R is not None:
            allR.append(R)
    allR.extend(terr)
    dflt, u_default = _series(I, "default", seeds(P)[0], 0.5, 481)
    if dflt is not None:
        allR.append(dflt)
    for rid in ("S2.control_static",):
        add(rows, rid, *(m_control_static(allR) if allR else _r(UNM, HARNESS, "no series")))
    pal_union = set()
    for R in allR:
        for k, p in (R.get("palettes") or {}).items():
            if k == "tremor":
                for q in p:
                    pal_union |= _pal(q)
            else:
                pal_union |= _pal(p)
    if allR:
        st4 = m_palette(allR, pal_union)
        c1, _ = I.hook("counters")
        dv = (c1 or {}).get("violations", 0) - (c0 or {}).get("violations", 0) if (c0 and c1) else None
        if st4[0] == PASS and dv:
            st4 = _r(FAIL, MOD, "RM_PaletteGuard counted %d violations during the run" % dv)
        add(rows, "L4.quantised", *st4)
    else:
        add(rows, "L4.quantised", UNM, HARNESS, "no series")
    for rid in ("W1.changed_only", "L5a.lead_count", "L5b.no_mixing", "L5c.boundary_moves", "L5d.front_clock"):
        add(rows, rid, *_worst(verd[rid]))
    Rs, u = _series(I, "territory_short_period", seeds(P)[0], 1.0, 2, period=60)
    add(rows, "L5d.period_clamped", *(u if Rs is None else m_front_clock(Rs, requested_short=60)))
    Rw, u = _series(I, "territory_swap", seeds(P)[0], P / STEPS_PER_TURN, 2)
    add(rows, "L5e.rank_order", *(u if (Rw is None or not terr) else m_rank_swap(terr[0], Rw)))
    for rid in ("L6a.tremor_cap", "L6b.tremor_fraction", "L6c.tremor_own_palette"):
        add(rows, rid, *_worst(tremV[rid]))

    sch = (I.settings or {}).get("dark_scheme") or {}
    Rd, u = _series(I, "dark", seeds(P)[0], 0.5, int(2 * float(sch.get("massPeriodSeconds", 120)) / 0.5) + 1)
    add(rows, "L8.dark_never_still", *(u if Rd is None else m_dark(Rd, float(sch.get("massPeriodSeconds", 120)))))
    Ru, u = _series(I, "unlit", seeds(P)[0], 0.5, 121)
    if Ru is None:
        add(rows, "L9.unlit_untouched", *u)
    else:
        ok = int(Ru.get("unlit_writes", -1)) == 0 and int(Ru.get("skipped_unlit_delta", 0)) > 0
        add(rows, "L9.unlit_untouched", PASS if ok else FAIL, MOD,
            "unlit fixture %s: writes %s, skippedUnlit +%s" % (Ru.get("unlit_id"), Ru.get("unlit_writes"), Ru.get("skipped_unlit_delta")))
    add(rows, "L11a.never_white", *(m_white(allR) if allR else _r(UNM, HARNESS, "no series")))
    wv, why = I.hook("series", scenario="white_scheme", t0=seeds(P)[0], dt=1.0, n=1)
    if wv is None or "valid" not in wv:
        add(rows, "L11b.white_scheme_rejected", UNM, HARNESS, "white_scheme probe unanswered: %s" % (why or wv))
    else:
        add(rows, "L11b.white_scheme_rejected", PASS if wv["valid"] is False else FAIL, MOD,
            "a scheme with a white entry is %s by Valid" % ("rejected" if wv["valid"] is False else "ACCEPTED"))
    Rn, u = _series(I, "narrator_alarm", seeds(P)[0], 0.25, 161)
    add(rows, "L12.narrator_outranks_alarm", *(u if Rn is None else m_narrator_wins(Rn)))
    Rg, u = _series(I, "gesture", seeds(P)[0], 0.25, 161)
    add(rows, "L13.gesture_restores", *(u if Rg is None else m_restore(Rg)))
    add(rows, "N1.narrator_envelope", *(u if Rg is None else m_envelope(Rg)))

    live = I.settings or {}
    ds = live.get("default_scheme") or {}
    if not live.get("settings") or not ds:
        add(rows, "D2.default_gentle_live", UNM, HARNESS, "settings probe unanswered: %s" % why_settings)
    else:
        d = dict(live["settings"])
        d["defaultScheme"] = ds.get("defName")
        d["schemes"] = {ds.get("defName"): {"palette": [tuple(c[:3]) for c in ds.get("palette") or []],
                                            "mayGoDark": bool(ds.get("mayGoDark")), "flasherCount": int(ds.get("flasherCount", 0))}}
        verdict = judge_defaults(d)
        if verdict[0] == PASS and disk_defaults:
            diff = [k for k in ("territoryPeriodSeconds", "territoryLeadShare", "tremorCap", "tremorMaxFraction")
                    if k in disk_defaults and abs(float(disk_defaults[k]) - float(d.get(k, -1))) > 1e-6]
            if diff:
                verdict = _r(INF, MOD, "live settings gentle but differ from the shipped defaults in %s (a saved Mod Setting?)" % diff)
        add(rows, "D2.default_gentle_live", *verdict)
    add(rows, "D3.no_light_show", *(u_default if dflt is None else m_light_show(dflt)))

    cost, why = I.hook("cost", n=200)
    if cost is None:
        add(rows, "C1.cost", UNM, HARNESS, "cost probe unanswered: %s (jawa/map_comp_timing cannot see MapComponentUpdate)" % why)
    else:
        n, ms = int(cost.get("fixtures", 0)), float(cost.get("ms_per_eval", -1))
        bar = COST_MS_PER_100 * max(1.0, n / 100.0)
        add(rows, "C1.cost", PASS if 0 <= ms <= bar else FAIL, MOD,
            "PROVISIONAL band: %.4f ms per Evaluate at %d fixtures (bar %.3f)" % (ms, n, bar))

    kt = kv_all.get("ProofTerritory") or {}
    vb = [r for r in rows if r["id"] in ("L5c.boundary_moves", "L6a.tremor_cap", "L5b.no_mixing")]
    if not kt or len(vb) < 3 or any(r["status"] not in (PASS, FAIL) for r in vb):
        add(rows, "X1.k_and_v_agree", UNM, HARNESS, "need both the ProofTerritory K row and the V rows measured")
    else:
        pairs = (("boundary_moves", "L5c.boundary_moves"), ("tremor_cap_held", "L6a.tremor_cap"), ("own_palette", "L5b.no_mixing"))
        st_of = dict((r["id"], r["status"]) for r in rows)
        dis = [(k, kt.get(k), v, st_of[v]) for k, v in pairs if (kt.get(k) == "True") != (st_of[v] == PASS)]
        add(rows, "X1.k_and_v_agree", FAIL if dis else PASS, HARNESS,
            "the mod's self-judgement and the independent measurement disagree: %s" % dis if dis else
            "ProofTerritory and the V rows agree on boundary, tremor cap and palette")


def l10(I, rows, pick, scheme):
    fid = I.fixture or ((pick or {}).get("fixtures") or [None])[0]
    ctl = (pick or {}).get("untaken")
    if fid is None:
        add(rows, "L10.real_time_while_paused", UNM, SITE, "no fixture to hold: give --fixture <ThingID> or build the pick hook")
        return
    mass = float((scheme or {}).get("massPeriodSeconds", 120.0))
    window = mass + 10.0
    was = I.clock()
    took = I.take(fid)
    if not took:
        add(rows, "L10.real_time_while_paused", UNM, SITE, "could not take over fixture %s" % fid)
        return
    runs, cvals = [], []
    try:
        for _ in range(2):
            I.pause()
            c1 = I.clock()
            vals = []
            t_end = I.wall() + window
            while I.wall() < t_end:
                vals.append(I.showing(fid))
                if ctl is not None:
                    cvals.append(I.showing(ctl))
                I.sleep(2.0)
            c2 = I.clock()
            moved = (c2.get("ticksGame") or 0) - (c1.get("ticksGame") or 0) if (c1.get("ticksGame") is not None and c2.get("ticksGame") is not None) else -1
            runs.append({"ticks_moved": moved, "values": vals})
    finally:
        I.release(fid)
        I.restore_speed(was)
    add(rows, "L10.real_time_while_paused", *m_l10(runs, cvals))


def reload_row(I, rows, pick, with_reload):
    if not with_reload:
        add(rows, "R1.save_reload_release", UNM, HARNESS, "not run: pass --with-reload (it reloads the session's game)")
        return
    fid = I.fixture or ((pick or {}).get("fixtures") or [None])[0]
    if fid is None:
        add(rows, "R1.save_reload_release", UNM, SITE, "no fixture to hold")
        return
    if not I.take(fid):
        add(rows, "R1.save_reload_release", UNM, SITE, "could not take over %s" % fid)
        return
    ok, why = I.save_reload("rm_proof_atmosphere")
    if not ok:
        I.release(fid)
        add(rows, "R1.save_reload_release", UNM, HARNESS, "save/reload failed: %s" % why)
        return
    held = I.is_taken(fid)
    I.release(fid)
    after = I.showing(fid)
    good = held and after is None
    add(rows, "R1.save_reload_release", PASS if good else FAIL, MOD,
        "after reload the claim %s; after Release it shows %r" % ("survived" if held else "was LOST", after))


def log_row(I, rows):
    t = I.log_budget()
    if not t.get("alive") or t.get("lost", 0) > 0:
        add(rows, "Z1.log_budget", UNM, HARNESS, "log not alive or %s journal entries lost" % t.get("lost"))
    elif t.get("ours"):
        add(rows, "Z1.log_budget", FAIL, MOD, "%d warn+ lines name the mod, e.g. %s" % (len(t["ours"]), t["ours"][:2]))
    else:
        add(rows, "Z1.log_budget", PASS, MOD, "0 warn+ lines from the mod over %d polls" % t.get("polls", 0))


# ---------------------------------------------------------------- the live instrument
def _kvargs(cmd, kw):
    return " ".join(["cmd=%s" % cmd] + ["%s=%s" % (k, kw[k]) for k in sorted(kw)])


class Live(object):
    def __init__(self, fixture=None):
        sys.path.insert(0, UTILS)
        import validation_core as vc   # imported here so --selftest and --offline never touch the game's paths
        self.vc = vc
        self.B = vc.Bridge()
        self.fixture = fixture
        self.settings = {}
        self.tap = None

    def _static(self, typ, method, args=None):
        kw = {"type": typ, "method": method}
        if args is not None:
            kw["args"] = args
        r = self.B.call("jawa/static_call", **kw) or {}
        if not r.get("success", True) or r.get("error"):
            return None, str(r.get("error") or r.get("message"))[:160]
        return r.get("result"), None

    def alive(self):
        try:
            rm = self.B.call("jawa/running_mods") or {}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "detail": "bridge unreachable: %s" % e}
        rm = rm.get("result", rm) if isinstance(rm, dict) else rm
        ids = [str(x).lower() for x in (rm.get("packageIds") or [])] or \
              [str(m.get("packageId", "")).lower() for m in (rm.get("mods") or []) if isinstance(m, dict)]
        if not ids:
            return {"ok": False, "detail": "running_mods answered no list"}
        return {"ok": PACKAGE_ID in ids, "detail": "%d mods running; %s %s" % (len(ids), PACKAGE_ID, "present" if PACKAGE_ID in ids else "ABSENT")}

    def log_revive(self):
        r = self.vc.log_revive(self.B)
        self.tap = self.vc.tap_start(self.B)
        return r

    def legacy(self, method):
        text, why = self._static(PROOF_TYPE, method, "go")
        if text in (None, ""):
            return None, "%s answered nothing: %s" % (method, why)
        if str(text).startswith("ERROR"):
            return None, "%s raised: %s" % (method, str(text)[:160])
        return dict(re.findall(r"(\w+)=(\S+)", str(text))), None

    def hook(self, cmd, **kw):
        text, why = self._static(PROOF_TYPE, "ProofSample", _kvargs(cmd, kw))
        if text in (None, ""):
            return None, why or "empty answer"
        try:
            o = json.loads(text)
        except ValueError:
            return None, "not JSON: %s" % str(text)[:120]
        if isinstance(o, dict) and o.get("error"):
            return None, o["error"]
        return o, None

    def clock(self):
        c = self.B.call("jawa/time_clock") or {}
        return c.get("result", c) if isinstance(c.get("result"), dict) else c

    def pause(self):
        self.B.call("jawa/set_game_speed", speed=0)

    def restore_speed(self, was):
        if not (was or {}).get("paused"):
            self.B.call("jawa/set_game_speed", speed=1)

    def wall(self):
        return time.time()

    def sleep(self, s):
        time.sleep(s)

    # RM_AtmosphericBaseAPI takes a Thing, which jawa/static_call cannot build from an id string: the hook resolves the
    # ThingID and calls the API itself (plan §2: hold / showing / release / is_taken)
    def showing(self, fid):
        o, _ = self.hook("showing", id=fid)
        v = (o or {}).get("showing")
        return None if v in (None, "", "null") else str(v)

    def take(self, fid):
        o, _ = self.hook("hold", id=fid)
        return bool((o or {}).get("ok"))

    def release(self, fid):
        self.hook("release", id=fid)

    def is_taken(self, fid):
        o, _ = self.hook("is_taken", id=fid)
        return bool((o or {}).get("taken"))

    def save_reload(self, name):
        s = self.B.call("rimworld/save_game", saveName=name) or {}
        if s.get("error"):
            return False, s.get("error")
        r = self.B.call("rimworld/load_game", saveName=name) or {}
        return (not r.get("error")), r.get("error")

    def log_budget(self):
        if self.tap is None:
            return {"alive": False}
        es = self.tap.since()
        ours = [str(e.get("Message", ""))[:160] for e in es
                if str(e.get("Level", "")).lower() in ("warning", "error", "exception")
                and re.search(r"AtmosphericBase|RM_Atmospheric|RM_Compositor|RM_Territory|RM_Tremor", str(e.get("Message", "")))]
        return {"alive": True, "lost": self.tap.lost, "polls": getattr(self.tap, "polls", 0), "ours": ours}


# ---------------------------------------------------------------- the stub instrument (a small model of the mod)
LAMP = [(204, 150, 92), (224, 168, 104), (244, 188, 118)]
FIRE = [(210, 158, 94), (234, 176, 106), (255, 196, 120)]
SUBSTRATE = (217, 217, 208)       # a vanilla standing lamp: near-white, but it is not ours (role S)
WHITE = (255, 255, 255)


def _h(a, b=0):
    x = (a * 2654435761 + b * 40503 + 12345) & 0xffffffff
    x ^= x >> 13
    x = (x * 1274126177) & 0xffffffff
    return x ^ (x >> 16)


def _f01(a, b):
    return _h(a, b) / 4294967296.0


class Stub(object):
    """Variants: good, phase5, off_palette, static_boundary, mixed, tremor30, white, no_restore, pause_fails, no_hook,
    no_fixtures, blind, leaky."""

    def __init__(self, variant="good", fixture=None):
        self.v = variant
        n = 0 if variant == "no_fixtures" else 20
        self.ids = list(range(101, 101 + n))
        self.pos = dict((i, (math.cos(k * 2.4) * (3 + k % 5), math.sin(k * 2.4) * (3 + k % 5))) for k, i in enumerate(self.ids))
        self.ticks, self.paused, self.now = 5000, False, 0.0
        self.taken, self.saved = set(), None
        self.fixture, self.settings = fixture, {}
        self.dirty = False
        self.cnt = {"violations": 0, "skippedUnlit": 0}

    # the model
    def mood_idx(self, i, t, mass=120.0):
        k = int(math.floor(t / (mass / 4.0) + _f01(i, 1) * 4))
        return k % 3

    def lead_set(self, t, period=900.0, swap=False):
        step = 0 if self.v == "static_boundary" else clock_step(t, period)
        cx = sum(p[0] for p in self.pos.values()) / len(self.pos)
        cz = sum(p[1] for p in self.pos.values()) / len(self.pos)
        order = sorted(self.ids, key=lambda i: (math.atan2(self.pos[i][1] - cz, self.pos[i][0] - cx), i))
        n, k = len(order), lead_count(len(order), 0.6)
        u = (step % STEPS_PER_TURN) / float(STEPS_PER_TURN) + 0.31
        start = min(n - 1, int(math.floor((u - math.floor(u)) * n)))
        lead = set(order[(start + j) % n] for j in range(k))
        return (set(self.ids) - lead) if swap else lead

    def tremor_at(self, t):
        frac, one_in, cap = (0.30, 1, 6) if self.v == "tremor30" else (0.04, 4, None)
        hits = []
        for i in self.ids:
            for c in range(3):
                sh = t + _f01(i ^ (c + 7), 17) * 30.0
                slot = int(math.floor(sh / 30.0))
                h = _h(i ^ (c + 7), slot)
                if h % one_in == 0 and sh - slot * 30.0 < 0.8:
                    hits.append((i, c, (h >> 8) % 3))
                    break
        cap = cap or max(1, int(math.floor(len(self.ids) * frac + 1e-4)))
        return hits[:cap]

    def frame(self, scenario, t, period=900.0):
        fx, contributors = [], 0
        if scenario in ("territory", "territory_swap", "territory_short_period", "tremor"):
            lead = self.lead_set(t, period, swap=(scenario == "territory_swap"))
            trem = dict((i, (c, j)) for i, c, j in self.tremor_at(t)) if scenario == "tremor" else {}
            contributors = 3 if scenario == "tremor" else 0
            for i in self.ids:
                o = 0 if i in lead else 1
                if i in trem:
                    c, j = trem[i]
                    col = [LAMP, FIRE, LAMP][c][j]
                    fx.append([i, col[0], col[1], col[2], o, "T", c])
                    continue
                pal = LAMP if (o == 0) != (self.v == "mixed" and o == 1) else FIRE
                if self.v == "mixed" and o == 1:
                    pal = LAMP
                col = pal[self.mood_idx(i, t, 120.0 if pal is LAMP else 40.0)]
                if self.v == "off_palette" and i == self.ids[3] and int(t) % 7 == 0:
                    col = (200, 140, 90)
                if self.v == "white" and i == self.ids[5]:
                    col = (230, 230, 230)
                fx.append([i, col[0], col[1], col[2], o, "L" if o == 0 else "O", -1])
        else:
            for i in self.ids:
                col = LAMP[self.mood_idx(i, t)]
                fx.append([i, col[0], col[1], col[2], -1, "M", -1])
        return fx, contributors

    def series(self, scenario, t0, dt, n, period=None):
        if scenario in ("gesture", "narrator_alarm") and self.v not in ("phase5", "no_restore"):
            return {"unknown_scenario": scenario}
        if scenario == "dark":
            return {"unsupported": "no shipped scheme mayGoDark (Lamplight and Fireflies never go dark)"}
        if scenario == "white_scheme":
            return {"valid": self.v == "white", "samples": []}
        P = max(MIN_PERIOD, float(period if period is not None else 900.0))
        out = {"period": P, "lead_share": 0.6, "lead_expected": lead_count(len(self.ids), 0.6),
               "lead_claimant": "atmosphericbase.proof.second" if scenario == "territory_swap" else "atmosphericbase.proof",
               "palettes": {"lead": LAMP, "other": FIRE, "tremor": [LAMP, FIRE, LAMP], "mood": LAMP}, "samples": [], "same_t_writes": 0}
        prev = None
        twin = []
        tg, D = t0 + 10.0, 10.0
        for k in range(int(n)):
            t = t0 + k * dt
            fx, contrib = self.frame("default" if scenario in ("gesture", "narrator_alarm", "unlit") else scenario, t, P)
            if scenario in ("gesture", "narrator_alarm"):
                twin.append([[f[0], f[1], f[2], f[3]] for f in fx])
                if tg <= t < tg + D:
                    u = (t - tg) / 2.0
                    w = (t - tg - 2.0) / 8.0
                    for f in fx:
                        base = (f[1], f[2], f[3])
                        if u <= 1.0:
                            c = tuple(int(round(b + (255 - b) * u)) for b in base)
                        else:
                            c = tuple(int(round(255 + (b - 255) * w)) for b in base)
                        f[1:4] = list(c)
                        f[5] = "N"
                elif t >= tg + D and self.v == "no_restore":
                    for f in fx:
                        c = LAMP[(LAMP.index((f[1], f[2], f[3])) + 1) % 3]
                        f[1:4] = list(c)
            if scenario == "unlit":
                f = fx[0]
                f[1:4], f[4], f[5] = list(SUBSTRATE), -1, "S"
            writes = 0 if prev is None else sum(1 for a, b in zip(prev, fx) if b[5] != "S" and a[1:4] != b[1:4])
            prev = fx
            out["samples"].append({"t": t, "step": clock_step(t, P), "fx": fx, "writes": writes,
                                   "contributors": contrib, "ctl": list(SUBSTRATE)})
        if scenario in ("gesture", "narrator_alarm"):
            out.update(t_g=tg, D=D, twin=twin)
        if scenario == "unlit":
            out.update(unlit_id=self.ids[0], unlit_writes=0, skipped_unlit_delta=int(n))
        if self.v == "leaky":
            self.dirty = True
        return out

    # the instrument interface
    def alive(self):
        return {"ok": True, "detail": "stub: 13 mods running; %s present" % PACKAGE_ID}

    def log_revive(self):
        return {"alive": True}

    def legacy(self, method):
        return dict((k, "True") for k in K_WANT[method]), None

    def hook(self, cmd, **kw):
        if self.v == "no_hook":
            return None, "No public static ProofSample with 1 params"
        if cmd == "pick":
            return {"fixtures": list(self.ids), "lit": len(self.ids), "spread": len(self.ids), "untaken": 999}, None
        if cmd == "snapshot":
            return {"fx": [[i] + list(SUBSTRATE if not self.dirty or i != self.ids[0] else LAMP[0]) for i in self.ids]}, None
        if cmd == "sanity":
            b = LAMP[0] if self.v == "blind" else LAMP[1]
            return {"lamp": self.ids[0], "forced": [LAMP[0], LAMP[1]], "a": LAMP[0], "b": b, "static_id": 999}, None
        if cmd == "settings":
            return {"settings": {"territoryPeriodSeconds": 900.0, "territoryLeadShare": 0.6, "territoryRagged": 0.08,
                                 "tremorCap": 3, "tremorMaxFraction": 0.04, "tremorFlickerSeconds": 0.8},
                    "default_scheme": {"defName": "RM_Scheme_Lamplight", "palette": LAMP, "mayGoDark": False,
                                       "flasherCount": 0, "massPeriodSeconds": 120.0}}, None
        if cmd == "counters":
            return dict(self.cnt), None
        if cmd == "cost":
            return {"ms_per_eval": 0.02, "fixtures": len(self.ids)}, None
        if cmd == "series":
            return self.series(kw["scenario"], float(kw["t0"]), float(kw["dt"]), int(kw["n"]), kw.get("period")), None
        return None, "unknown cmd %s" % cmd

    def clock(self):
        return {"ticksGame": self.ticks, "paused": self.paused}

    def pause(self):
        self.paused = self.v != "pause_fails"

    def restore_speed(self, was):
        self.paused = bool((was or {}).get("paused"))

    def wall(self):
        return self.now

    def sleep(self, s):
        self.now += s
        if not self.paused:
            self.ticks += int(60 * s)

    def showing(self, fid):
        return ("RM_Scheme_Lamplight:%d" % self.mood_idx(fid, self.now + 1000.0)) if fid in self.taken else None

    def take(self, fid):
        if fid in self.ids:
            self.taken.add(fid)
            return True
        return False

    def release(self, fid):
        self.taken.discard(fid)

    def is_taken(self, fid):
        return fid in self.taken

    def save_reload(self, name):
        return True, None

    def log_budget(self):
        return {"alive": True, "lost": 0, "polls": 3, "ours": []}


# ---------------------------------------------------------------- selftest
def _st(rows):
    return dict((r["id"], (r["status"], r["class"])) for r in rows)


EXPECT = {   # variant -> {row: (status, class)} that variant MUST produce
    "good": {"S1.sampler_sees": (PASS, HARNESS), "S2.control_static": (PASS, HARNESS), "S3.deterministic": (PASS, HARNESS),
             "L4.quantised": (PASS, MOD), "W1.changed_only": (PASS, MOD), "L5a.lead_count": (PASS, MOD),
             "L5b.no_mixing": (PASS, MOD), "L5c.boundary_moves": (PASS, MOD), "L5d.front_clock": (PASS, MOD),
             "L5d.period_clamped": (PASS, MOD), "L5e.rank_order": (PASS, MOD), "L6a.tremor_cap": (PASS, MOD),
             "L6b.tremor_fraction": (PASS, MOD), "L6c.tremor_own_palette": (PASS, MOD), "L8.dark_never_still": (UNM, MOD),
             "L9.unlit_untouched": (PASS, MOD), "L10.real_time_while_paused": (PASS, MOD), "L11a.never_white": (PASS, MOD),
             "L11b.white_scheme_rejected": (PASS, MOD), "L12.narrator_outranks_alarm": (UNM, HARNESS),
             "L13.gesture_restores": (UNM, HARNESS), "N1.narrator_envelope": (UNM, HARNESS), "D2.default_gentle_live": (PASS, MOD),
             "D3.no_light_show": (PASS, MOD), "C1.cost": (PASS, MOD), "X1.k_and_v_agree": (PASS, HARNESS),
             "R1.save_reload_release": (PASS, MOD), "R2.left_as_found": (PASS, MOD), "Z1.log_budget": (PASS, MOD)},
    "phase5": {"L12.narrator_outranks_alarm": (PASS, MOD), "L13.gesture_restores": (PASS, MOD), "N1.narrator_envelope": (PASS, MOD)},
    "off_palette": {"L4.quantised": (FAIL, MOD)},
    "static_boundary": {"L5c.boundary_moves": (FAIL, MOD), "X1.k_and_v_agree": (FAIL, HARNESS)},
    "mixed": {"L5b.no_mixing": (FAIL, MOD), "L4.quantised": (PASS, MOD)},
    "tremor30": {"L6b.tremor_fraction": (FAIL, MOD), "L6a.tremor_cap": (PASS, MOD)},
    "white": {"L11a.never_white": (FAIL, MOD), "L11b.white_scheme_rejected": (FAIL, MOD)},
    "no_restore": {"L13.gesture_restores": (FAIL, MOD), "N1.narrator_envelope": (PASS, MOD)},
    "pause_fails": {"L10.real_time_while_paused": (UNM, HARNESS)},
    "no_hook": dict([(r, (UNM, HARNESS)) for r in V_ROWS] + [("K.ProofTerritory", (PASS, MOD))]),
    "no_fixtures": dict((r, (UNM, SITE)) for r in V_ROWS),
    "blind": dict([("S1.sampler_sees", (FAIL, HARNESS))] + [(r, (UNM, HARNESS)) for r in V_ROWS]),
    "leaky": {"R2.left_as_found": (FAIL, MOD)},
}


def metric_controls():
    """Synthetic negative controls for the pure metrics: each must refuse the bad series."""
    out = []

    def S(ts, cols, owner=-1, role="M", n=4):
        return [{"t": t, "fx": [[i, c[0], c[1], c[2], owner, role, -1] for i in range(n)], "writes": 0, "contributors": 0}
                for t, c in zip(ts, cols)]
    ts = [k * 0.5 for k in range(481)]
    black = S(ts, [(0, 0, 0)] * len(ts))
    out.append(("m_dark black still", m_dark({"samples": black}, 120.0)[0], FAIL))
    flick = S(ts, [LAMP[k % 2] for k in range(len(ts))])
    out.append(("m_light_show 0.5 s flicker", m_light_show({"samples": flick})[0], FAIL))
    wr = S(ts[:3], [LAMP[0], LAMP[1], LAMP[1]])
    out.append(("m_writes undercount", m_writes({"samples": wr, "same_t_writes": 0})[0], FAIL))
    out.append(("m_writes same-t writes", m_writes({"samples": S(ts[:2], [LAMP[0]] * 2), "same_t_writes": 3})[0], FAIL))
    off = [{"t": 0.0, "step": 0, "fx": [[1, 0, 0, 0, 0, "L"], [2, 0, 0, 0, 1, "O"]]},
           {"t": 1.0, "step": 0, "fx": [[1, 0, 0, 0, 1, "O"], [2, 0, 0, 0, 0, "L"]]}]
    out.append(("m_front_clock flip off-boundary", m_front_clock({"samples": off, "period": 900.0})[0], FAIL))
    out.append(("m_front_clock 60 s unclamped", m_front_clock({"samples": off, "period": 60.0}, requested_short=60)[0], FAIL))
    lead = [{"t": 0.0, "fx": [[i, 0, 0, 0, 0, "L"] for i in range(10)]}]
    out.append(("m_lead one side empty", m_lead({"samples": lead, "lead_share": 0.6})[0], FAIL))
    out.append(("m_boundary short series", m_boundary({"samples": off, "period": 900.0, "lead_share": 0.6})[0], UNM))
    trem = {"samples": S([k * 1.0 for k in range(300)], [LAMP[0]] * 300), "palettes": {"tremor": [LAMP]}}
    out.append(("m_tremor coarse dt", m_tremor(trem, 0.8)[0][0], UNM))
    env = {"t_g": 0.0, "D": 10.0, "palettes": {"lead": LAMP},
           "samples": S([k * 0.5 for k in range(20)], [WHITE] * 2 + [LAMP[0]] * 8 + [WHITE] * 10)}
    out.append(("m_envelope brightens while dimming", m_envelope(env)[0], FAIL))
    ctl = [{"samples": [{"t": 0, "fx": [], "ctl": [1, 2, 3]}, {"t": 1, "fx": [], "ctl": [1, 2, 4]}]}]
    out.append(("m_control_static control moves", m_control_static(ctl)[0], FAIL))
    out.append(("m_l10 ticks moved", m_l10([{"ticks_moved": 60, "values": ["a", "b"]}], [])[0], UNM))
    out.append(("m_l10 frozen", m_l10([{"ticks_moved": 0, "values": ["a"] * 40}], [])[0], FAIL))
    out.append(("m_l10 control reports a scheme", m_l10([{"ticks_moved": 0, "values": ["a", "b"]}], ["x:0"])[0], FAIL))
    cs = "public float territoryPeriodSeconds = 900f; public float territoryLeadShare = 0.6f; public float territoryRagged = 0.08f;" \
         " public int tremorCap = 3; public float tremorMaxFraction = 0.2f; public float tremorFlickerSeconds = 0.8f;"
    xml = "<Defs><X><defName>A</defName><palette><li>(204,150,92,0)</li></palette></X></Defs>"
    out.append(("judge_defaults tremor 0.2", judge_defaults(read_defaults(cs, xml, 'DefaultSchemeDefName = "A"'))[0], FAIL))
    xml_w = "<Defs><X><defName>A</defName><palette><li>(250,250,250,0)</li></palette><flasherCount>2</flasherCount></X></Defs>"
    out.append(("judge_defaults white + flashers", judge_defaults(read_defaults(cs.replace("0.2f", "0.04f"), xml_w, 'DefaultSchemeDefName = "A"'))[0], FAIL))
    out.append(("judge_defaults gentle", judge_defaults(read_defaults(cs.replace("0.2f", "0.04f"), xml, 'DefaultSchemeDefName = "A"'))[0], PASS))
    return out


def selftest():
    bad = []
    for name, got, want in metric_controls():
        print("control %-40s %-10s (want %s)" % (name, got, want))
        if got != want:
            bad.append("control %s: %s != %s" % (name, got, want))
    report = {}
    for variant in sorted(EXPECT):
        print("\n== stub variant: %s" % variant)
        rows = []
        proof(Stub(variant), rows, with_reload=True)
        got = _st(rows)
        report[variant] = rows
        for rid, want in sorted(EXPECT[variant].items()):
            if got.get(rid) != want:
                bad.append("%s %s: got %s want %s" % (variant, rid, got.get(rid), want))
        if variant == "good":
            stray = [r for r in rows if r["status"] == FAIL]
            if stray:
                bad.append("good model has FAIL rows %s" % [r["id"] for r in stray])
        if any(r["status"] == PASS and "not built" in str(r["detail"]) for r in rows):
            bad.append("%s: a 'not built' row reads PASS" % variant)
    print("\nselftest: %d variants, %d metric controls, %s" % (len(EXPECT), len(metric_controls()), "OK" if not bad else "FAILED"))
    for b in bad:
        print("  " + b)
    return (0 if not bad else 1), report


def write_out(out_dir, mode, rows):
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "proof_atmosphere_%s_%s.json" % (mode, time.strftime("%Y%m%dT%H%M%S")))
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"mode": mode, "rows": rows}, f, indent=1)
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true", help="stub bridge only: good and bad models, negative controls")
    ap.add_argument("--offline", action="store_true", help="disk rows only (P1, D1)")
    ap.add_argument("--fixture", help="ThingID of a lit lamp for L10/R1 when the pick hook is missing")
    ap.add_argument("--with-reload", action="store_true", help="run R1 (saves and reloads the current game)")
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()
    if a.selftest:
        rc, report = selftest()
        if os.path.isdir(os.path.dirname(a.out.rstrip("/"))):
            print("wrote %s" % write_out(a.out, "selftest", report))
        return rc
    rows = []
    d = offline_rows(rows)
    if not a.offline:
        try:
            proof(Live(a.fixture), rows, with_reload=a.with_reload, disk_defaults=d)
        except Exception as e:  # noqa: BLE001 -- a bridge fault ends the run as a HARNESS row, never as a silent stack
            add(rows, "P9.run_aborted", UNM, HARNESS, "%s: %s" % (type(e).__name__, e))
    n = dict((s, sum(1 for r in rows if r["status"] == s)) for s in (PASS, FAIL, UNM, INF))
    print("\n%d rows: %s" % (len(rows), n))
    print("wrote %s" % write_out(a.out, "offline" if a.offline else "live", rows))
    return 1 if n[FAIL] else 0


if __name__ == "__main__":
    sys.exit(main())
