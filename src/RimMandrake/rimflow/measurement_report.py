#!/usr/bin/env python3
"""measurement_report.py - RIMMANDRAKE_PRINT_MEASUREMENT_REPORT_BESIDE_EVERY_GREEN_CHECK (step 3 of
RIMMANDRAKE_ENACT_INVENTION_WHEN_BARS_CONFLICT_GRADIENT_TOO_EASY): one report any check, rescue instrument or certificate
can print, so a green is read with its evidence beside it.

Per check it states:
  parity       the agreement number between a copy of an instrument and the game's own numbers, and every disagreement
               (explained, or named unexplained); or {"state": "UNMEASURED", "why": ...} when nothing compares them
  family       what was sampled: its generator and how many cases
  exclusions   what the family leaves out (an empty list needs exclusions_none_why: silence is not "none")
  worst        the worst case and the limit it is read against ("at least" or "at most"), with the headroom
  regressions  the old checks and challenge cases (the instrument-can-fail controls), each PASS / FAIL / UNRUN
  source       the source commit, the settings and the instrument version it ran on, so a stale report can be told

It is a report, never a gate: a worst case near or past its limit is printed as such and is a reason to look; the
check's own verdict is never rewritten and no margin threshold lives here.

    python3 src/RimMandrake/rimflow/measurement_report.py gss-live-end      runs Gimme Some Slack's live-end sweep (~3 min)
                                                                             and prints its report
Exit 0 report printed; 2 a reading was refused or a line could not be read (named on stderr, nothing printed as a report).
"""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

REQUIRED = ("check", "verdict", "parity", "family", "exclusions", "worst", "regressions", "source")
VERDICTS = ("PASS", "FAIL")
REGRESSION_RESULTS = ("PASS", "FAIL", "UNRUN")
READS = ("at least", "at most")


class Refused(ValueError):
    pass


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def build(reading):
    """-> the report for one check, or Refused naming every field that is missing or malformed."""
    if not isinstance(reading, dict):
        raise Refused("a reading is an object, not %r" % type(reading).__name__)
    errs = ["no %s" % k for k in REQUIRED if k not in reading]
    if errs:
        raise Refused("%s: %s" % (reading.get("check", "?"), "; ".join(errs)))
    if reading["verdict"] not in VERDICTS:
        errs.append("verdict %r is not PASS or FAIL" % reading["verdict"])
    p = reading["parity"]
    if not isinstance(p, dict):
        errs.append("parity is not an object")
    elif p.get("state") == "UNMEASURED":
        if not str(p.get("why") or "").strip():
            errs.append("parity UNMEASURED names no cause (why)")
    elif not _num(p.get("agreement")) or not isinstance(p.get("disagreements"), list):
        errs.append("parity needs agreement (a number) and disagreements (a list), or state UNMEASURED with why")
    f = reading["family"]
    c = f.get("cases") if isinstance(f, dict) else None
    counted = isinstance(c, int) and not isinstance(c, bool) and c > 0
    unm = isinstance(c, dict) and c.get("state") == "UNMEASURED" and str(c.get("why") or "").strip()
    if not (isinstance(f, dict) and str(f.get("generator") or "").strip() and (counted or unm)):
        errs.append("family needs generator and cases (a whole number above 0, or {state: UNMEASURED, why})")
    ex = reading["exclusions"]
    if not isinstance(ex, list):
        errs.append("exclusions is not a list")
    elif not ex and not str(reading.get("exclusions_none_why") or "").strip():
        errs.append("exclusions is empty with no exclusions_none_why (silence is not 'none')")
    w = reading["worst"]
    if not (isinstance(w, dict) and _num(w.get("value")) and _num(w.get("limit")) and w.get("reads") in READS):
        errs.append("worst needs value and limit (numbers) and reads (%s)" % " or ".join(READS))
    rg = reading["regressions"]
    if not isinstance(rg, list) or any(not (isinstance(g, dict) and str(g.get("name") or "").strip()
                                            and g.get("result") in REGRESSION_RESULTS) for g in rg):
        errs.append("regressions is a list of {name, result: %s}" % "/".join(REGRESSION_RESULTS))
    s = reading["source"]
    if not isinstance(s, dict):
        errs.append("source is not an object")
    else:
        errs += ["source has no %s" % k for k in ("commit", "settings", "instrument") if k not in s or s[k] in (None, "")]
    if errs:
        raise Refused("%s: %s" % (reading["check"], "; ".join(errs)))
    rep = json.loads(json.dumps(reading))
    room = w["value"] - w["limit"] if w["reads"] == "at least" else w["limit"] - w["value"]
    rep["worst"]["headroom"] = round(room, 9)
    return rep


def render(reports):
    out = []
    for r in reports:
        w, p, f, s = r["worst"], r["parity"], r["family"], r["source"]
        out.append("## %s: %s" % (r["check"], r["verdict"]))
        if r.get("observed"):
            out.append("  observed     %s" % r["observed"])
        if p.get("state") == "UNMEASURED":
            out.append("  parity       UNMEASURED: %s" % p["why"])
        else:
            out.append("  parity       agreement %s, %d disagreement(s)" % (p["agreement"], len(p["disagreements"])))
            for dz in p["disagreements"]:
                why = dz.get("explained") if isinstance(dz, dict) else None
                out.append("               - %s: %s" % ((dz or {}).get("what") if isinstance(dz, dict) else dz,
                                                       why or "unexplained"))
        c = f["cases"]
        out.append("  family       %s (%s)" % (f["generator"], "%d cases" % c if isinstance(c, int) else
                                               "cases UNMEASURED: %s" % c["why"]))
        out.append("  exclusions   %s" % ("; ".join(r["exclusions"]) or "none: %s" % r.get("exclusions_none_why")))
        flag = "  PAST ITS LIMIT" if w["headroom"] < 0 else ""
        out.append("  worst        %s, read %s %s: headroom %s%s" % (w["value"], w["reads"], w["limit"],
                                                                     ("%.6f" % w["headroom"]).rstrip("0").rstrip("."),
                                                                     flag))
        out.append("  regressions  %s" % ("; ".join("%s %s" % (g["result"], g["name"]) for g in r["regressions"])
                                         or "none run"))
        out.append("  source       commit %s, instrument %s, settings %s" % (
            s["commit"], s["instrument"], json.dumps(s["settings"], sort_keys=True)))
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------- Gimme Some Slack's live-end sweep

GSS_SWEEP = os.path.join("src", "RimMandrake", "GimmeSomeSlack", "selftest_gss_live_end_sweep.py")
GSS_LIB = os.path.join("src", "RimMandrake", "Utils", "mockups", "messy_conduit")
GSS_PARITY = {"state": "UNMEASURED",
              "why": "the sweep runs the Python copy (Utils/mockups/messy_conduit/live_end_lay.py) of Core/CordLiveEnd.cs; "
                     "no instrument compares the copy's numbers with the game's own (the C# suite "
                     "SelfTest/LiveEndSweepChecks.cs sweeps the game's cords on its own grid)"}
_F = r"(-?[0-9.]+)"
# check -> (line regex, reading built from g = (the line,) + its groups, so g[1] is the verdict); the families and exclusions are the sweep's own declared bounds
# (its docstring), not measured here
GSS_LINES = [
    ("whip", r"^(PASS|FAIL) whip: the bend wave never bends a straight cord under %s \(tail 0\.7: %s, tail 0\.95: %s; "
             r"30 seeds x 20 s\)" % (_F, _F, _F),
     lambda g, st: {"worst": {"value": min(float(g[3]), float(g[4])), "limit": float(g[2]), "reads": "at least"},
                "family": {"generator": "dead straight cords, tails 0.7 and 0.95, 30 seeds x 20 s of the bend-wave whip",
                           "cases": 60},
                "exclusions": ["cords that start bent", "tails other than 0.7 and 0.95", "runs longer than 20 s"],
                "observed": "tightest bend: tail 0.7 %s, tail 0.95 %s" % (g[3], g[4])}),
    ("shot", r"^(PASS|FAIL) shot: a fitting under %s behind the end lies still, from %s .*\(still up to %s, whipping "
             r"from %s, other outcomes (\[.*\])\)" % (_F, _F, _F, _F),
     lambda g, st: {"worst": {"value": float(g[5]), "limit": float(g[3]), "reads": "at least"},
                "family": {"generator": "a fitting on the conduit's own line, distances behind the cut end",
                           "cases": {"state": "UNMEASURED", "why": "the sweep does not print how many distances it tried"}},
                "exclusions": ["fittings off the conduit's line (the poses checks)"],
                "observed": "still up to %s, whipping from %s, other outcomes %s" % (g[4], g[5], g[6])}),
    ("poses, lay alone", r"^(PASS|FAIL) poses: ([0-9]+) fitting poses .* \(the lay alone, no fitting body\): .*"
                         r"tightest bend %s; unlaid (\[.*\])" % _F,
     # the sweep's own bar: worst >= 1.5 * live_end_lib.MIN_BEND_R
     lambda g, st: {"worst": {"value": float(g[3]), "limit": round(1.5 * st["MIN_BEND_R"], 9), "reads": "at least"},
                "family": {"generator": "a fitting 0.3-2.5 cells round the conduit end, facing any way", "cases": int(g[2])},
                "exclusions": ["the fitting's own body (the two checks below)", "fittings nearer than 0.3 or beyond 2.5 cells"],
                "observed": "unlaid %s" % g[4]}),
    ("poses, box/plate/strip", r"^(PASS|FAIL) poses, the fitting a box, plate or strip: ([0-9]+) of ([0-9]+) unlaid, "
                               r"every one with the fitting's middle within %s cell of the end's run \(limit %s; the grid's "
                               r"nearest is %s\)" % (_F, _F, _F),
     lambda g, st: {"worst": {"value": float(g[4]), "limit": float(g[5]), "reads": "at most"},
                "family": {"generator": "the same poses with a box, plate or strip fitting's body there", "cases": int(g[3])},
                "exclusions": ["machine plugs (the next check)", "fittings nearer than 0.3 or beyond 2.5 cells"],
                "observed": "%s of %s unlaid; the C# suite's grid nearest %s" % (g[2], g[3], g[6])}),
    ("poses, machine plug", r"^(PASS|FAIL) poses, the fitting a machine's plug: ([0-9]+) of ([0-9]+) unlaid, ([0-9]+) with "
                            r"the machine's footprint ON the end's run, the rest within %s cell of it \(limit %s\)" % (_F, _F),
     lambda g, st: {"worst": {"value": float(g[5]), "limit": float(g[6]), "reads": "at most"},
                "family": {"generator": "the same poses with a machine's footprint there", "cases": int(g[3])},
                "exclusions": ["box, plate and strip fittings (the check above)", "fittings nearer than 0.3 or beyond 2.5 cells"],
                "observed": "%s of %s unlaid, %s with the footprint on the run" % (g[2], g[3], g[4])}),
]
# the instrument-can-fail lines: each is a regression of the check it guards
GSS_CONTROLS = [
    ("whip", r"^(PASS|FAIL) whip can fail: ", "the old sideways whip folds a straight 0.7 tail under the bar"),
    ("poses, lay alone", r"^(PASS|FAIL) poses: the tied loop is used on none of them", "the tied loop is used on no pose"),
    ("poses, lay alone", r"^(PASS|FAIL) can fail: a hooked cord", "a hooked cord is refused by the bars and laid again"),
]


def gss_live_end_readings(text, source):
    """The sweep's printed lines -> (readings, unread): one reading per check line it matched, and every PASS/FAIL line
    it could not read (never dropped, never zeroed)."""
    lines = [ln for ln in text.splitlines() if re.match(r"^(PASS|FAIL) ", ln)]
    used, readings = set(), {}
    for name, rx, make in GSS_LINES:
        for i, ln in enumerate(lines):
            m = re.match(rx, ln)
            if m:
                g = (m.group(0),) + m.groups()
                r = dict(make(g, source.get("settings") or {}), check=name, verdict=g[1], parity=dict(GSS_PARITY), regressions=[], source=source)
                readings[name] = r
                used.add(i)
                break
    for name, rx, what in GSS_CONTROLS:
        for i, ln in enumerate(lines):
            m = re.match(rx, ln)
            if m and name in readings:
                readings[name]["regressions"].append({"name": what, "result": m.group(1)})
                used.add(i)
                break
    unread = [ln for i, ln in enumerate(lines) if i not in used]
    return list(readings.values()), unread


def _sha(paths):
    h = hashlib.sha256()
    for p in sorted(paths):
        with open(p, "rb") as fh:
            h.update(fh.read())
    return "sha256:" + h.hexdigest()[:16]


def gss_source(root=REPO):
    files = [os.path.join(root, GSS_SWEEP)] + [os.path.join(root, GSS_LIB, n) for n in
                                                ("live_end_lay.py", "live_end_lib.py", "live_end_sweep.py")]
    r = subprocess.run(["git", "-C", root, "log", "-1", "--format=%H", "--"] + [os.path.relpath(f, root) for f in files],
                       capture_output=True, text=True, timeout=60)
    commit = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
    sys.path.insert(0, os.path.join(root, GSS_LIB))
    sys.path.insert(0, os.path.dirname(os.path.join(root, GSS_SWEEP)))
    import live_end_lay as Y  # noqa: E402
    import live_end_lib as L  # noqa: E402
    import selftest_gss_live_end_sweep as SW  # noqa: E402
    return {"commit": commit, "instrument": _sha(files),
            "settings": {"LIVE_BEND_R": Y.LIVE_BEND_R, "MIN_BEND_R": L.MIN_BEND_R, "BOX_CROWD": SW.BOX_CROWD,
                         "MACHINE_CROWD": SW.MACHINE_CROWD}}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] != ["gss-live-end"]:
        print(__doc__.strip().splitlines()[-3], file=sys.stderr)
        return 2
    src = gss_source()
    if not src["commit"]:
        print("REFUSED: the sweep's source commit could not be read (git log)", file=sys.stderr)
        return 2
    p = subprocess.run([sys.executable, os.path.join(REPO, GSS_SWEEP)], capture_output=True, text=True, timeout=900)
    readings, unread = gss_live_end_readings(p.stdout, src)
    if unread or not readings:
        print("REFUSED: %d line(s) of the sweep could not be read: %s" % (len(unread), unread or "no check line at all"),
              file=sys.stderr)
        return 2
    try:
        reports = [build(r) for r in readings]
    except Refused as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2
    print("# Measurement report: Gimme Some Slack live-end sweep (exit %d; %s)" % (
        p.returncode, (p.stdout.strip().splitlines() or ["no summary line"])[-1]))
    print()
    print(render(reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
