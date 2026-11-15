#!/usr/bin/env python3
"""maturation_convergence.py: does each mod converge, round over round, at each judging stage of the Maturation Pipeline?

Item RIMMANDRAKE_MEASURE_MATURATION_CONVERGENCE_PER_ROUND. MATURATION_NOW counted how many times a stage ran ("Stage 3 has
run 6 times") and nothing said whether the runs were getting anywhere. This reads the records already on disk, with no
model and no tokens, and gives per mod, per round of each judging stage, the findings new, fixed and still open, and one
word per mod per stage.

Records (each parsed, never counted by grep):
  Stage 3   design/concepts/<Mod>/stage.json coverage_rounds, one per coverage judge (coverage_judge.record_round):
            open = gaps; new = gaps - tags.unfixed (first + changed + regression + late); fixed = the previous measured
            round's open - this round's unfixed. A judge the budget charges with no round on file (before rounds were
            kept), a round that is not a dict, a gap count that is not a number, a verdict other than covered/not_covered
            or an error is an UNMEASURED round. coverage_fixes.json claims against a judge ride on that round (fix_claims).
  Stage 4+5 version/blind_challenge/cycle_N/lane2/faults.json, cycles 1..the highest on disk: found = faults; new = ids no
            earlier cycle had; fixed = status FIXED...; open = class Problem... not FIXED. A cycle with no faults.json, an
            empty or broken one, or a skipped cycle number is an UNMEASURED round. An empty faults list is a measured 0.
  Stage 6   version/in_game/visit_N/SUMMARY.md Exit block (maturation.ingame_exit_block): ingame_rows pass / fail /
            unmeasured and strange_open; open = fail + unmeasured + strange_open; new = tests not passing that passed or
            were absent the visit before, plus strange_open; fixed = tests not passing the visit before that pass now, plus
            the previous strange_open. No Exit block, or one with no ingame_rows, is an UNMEASURED round.

The word, read on the measured rounds alone (a missing round is shown as UNMEASURED and named, never filled in):
  UNMEASURED  no measured round, or the latest measured round has something open and there is only one measured round
  CONVERGING  the latest measured round has nothing open, or open fell from the round before
  DIVERGING   three measured rounds or more and new findings did not fall over the last three (n-2 <= n-1 <= n, n > 0),
              or open rose from the round before
  FLAT        otherwise (open the same as the round before)

The one behaviour: needs_lines() gives a Needs Conductor line, with the numbers, for every DIVERGING stage, and
annotate_reading() puts them in the Dispatch tick's reading. It pauses nothing and changes no bar.

    python3 src/RimMandrake/Utils/maturation_convergence.py [--root DIR] [--json | --print]
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONCEPTS = os.path.join("design", "concepts")
BLIND_DIR = os.path.join("version", "blind_challenge")
INGAME_DIR = os.path.join("version", "in_game")
JUDGE_PREFIX = "rm-coverage-judge-"     # coverage_judge.UNIT_PREFIX
VERDICTS = ("covered", "not_covered")
STAGES = (("3", "Offline build"), ("4+5", "Blind challenge"), ("6", "In-game"))
UNM = "UNMEASURED"
CONV, FLAT, DIV = "CONVERGING", "FLAT", "DIVERGING"
SOURCE = "maturation_convergence.py"


def _read(p):
    """-> (text, None), or (None, why) when the file is missing or unreadable."""
    if not os.path.isfile(p):
        return None, "no %s" % os.path.basename(p)
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read(), None
    except OSError as e:
        return None, "%s unreadable: %s" % (os.path.basename(p), e)


def _json(p):
    """-> (data, None), or (None, why): missing, empty and not-JSON each say so."""
    t, why = _read(p)
    if why:
        return None, why
    if not t.strip():
        return None, "%s is empty" % os.path.basename(p)
    try:
        return json.loads(t), None
    except ValueError as e:
        return None, "%s is not JSON (%s)" % (os.path.basename(p), str(e)[:60])


def _int(x):
    return x if isinstance(x, int) and not isinstance(x, bool) and x >= 0 else None


def _unm(n, why, **kw):
    r = {"round": n, "measured": False, "why": why, "new": None, "fixed": None, "open": None}
    r.update(kw)
    return r


# Stage 3: coverage judge rounds

def stage3(d):
    st, why = _json(os.path.join(d, "stage.json"))
    if why:
        return [], why
    if not isinstance(st, dict):
        return [], "stage.json is not an object"
    recorded = st.get("coverage_rounds") or []
    if not isinstance(recorded, list):
        return [], "coverage_rounds is not a list"
    known = {r.get("judge") for r in recorded if isinstance(r, dict)}
    legacy = {}
    charges = (st.get("budget") or {}).get("charges") if isinstance(st.get("budget"), dict) else None
    for c in charges if isinstance(charges, list) else []:
        ref = c.get("ref") if isinstance(c, dict) else None
        if isinstance(ref, str) and ref.startswith(JUDGE_PREFIX) and ref not in known and ref not in legacy:
            legacy[ref] = str(c.get("at") or "")
    claims = {}
    fx, _ = _json(os.path.join(d, "coverage_fixes.json"))
    if isinstance(fx, dict) and isinstance(fx.get("claims"), list):
        claims[fx.get("against")] = len(fx["claims"])
    out = [{"judge": ref, "at": at, "legacy": True} for ref, at in sorted(legacy.items(), key=lambda kv: kv[1])]
    out += list(recorded)
    rows, prev = [], None
    for i, r in enumerate(out, 1):
        if not isinstance(r, dict):
            rows.append(_unm(i, "round is not an object"))
            prev = None
            continue
        base = {"judge": r.get("judge"), "at": r.get("at"), "fix_claims": claims.get(r.get("judge"))}
        gaps, tags = _int(r.get("gaps")), r.get("tags")
        if r.get("legacy"):
            why = "judge charged with no round on file"
        elif r.get("verdict") not in VERDICTS:
            why = "verdict %r" % (r.get("verdict"),)
        elif r.get("error"):
            why = "error: %s" % str(r.get("error"))[:60]
        elif gaps is None:
            why = "gap count %r is not a number" % (r.get("gaps"),)
        elif not isinstance(tags if tags is not None or gaps else {}, dict):
            why = "tags %r are not counts" % (tags,)
        elif any(_int(v) is None for v in (tags or {}).values()):
            why = "a tag count is not a number"
        else:
            why = None
        if why:
            rows.append(_unm(i, why, **base))
            prev = None
            continue
        unfixed = min(_int((tags or {}).get("unfixed")) or 0, gaps)
        rows.append(dict(base, round=i, measured=True, open=gaps, new=gaps - unfixed,
                         fixed=None if prev is None else max(prev - unfixed, 0)))
        prev = gaps
    return rows, None


# Stage 4+5: blind challenge cycles

def _numbered(d, pat):
    out = []
    for f in os.listdir(d) if os.path.isdir(d) else []:
        m = re.match(pat, f)
        if m and os.path.isdir(os.path.join(d, f)):
            out.append(int(m.group(1)))
    return sorted(out)


def stage45(d):
    bd = os.path.join(d, BLIND_DIR)
    have = _numbered(bd, r"cycle_(\d+)$")
    if not have:
        return [], "no blind challenge cycle on disk"
    rows, seen = [], set()
    for n in range(1, max(have) + 1):
        if n not in have:
            rows.append(_unm(n, "no cycle_%d folder" % n))
            continue
        data, why = _json(os.path.join(bd, "cycle_%d" % n, "lane2", "faults.json"))
        fl = data.get("faults") if isinstance(data, dict) else data
        if not why and not isinstance(fl, list):
            why = "faults is not a list"
        if not why and not all(isinstance(x, dict) for x in fl):
            why = "a fault is not an object"
        if why:
            rows.append(_unm(n, why))
            continue
        ids = [str(x.get("id")) for x in fl]
        fixed = sum(1 for x in fl if str(x.get("status") or "").upper().startswith("FIXED"))
        opn = sum(1 for x in fl if str(x.get("class") or x.get("cls") or "").startswith("Problem")
                  and not str(x.get("status") or "").upper().startswith("FIXED"))
        rows.append({"round": n, "measured": True, "found": len(fl), "new": sum(1 for i in ids if i not in seen),
                     "fixed": fixed, "open": opn})
        seen.update(ids)
    return rows, None


# Stage 6: in-game visits

def stage6(d):
    vd = os.path.join(d, INGAME_DIR)
    have = _numbered(vd, r"visit_(\d+)$")
    if not have:
        return [], "no in-game visit on disk"
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
    import maturation as M     # noqa: E402  (lazy: maturation imports maturation_now, which imports this)
    rows, prev = [], None
    for n in range(1, max(have) + 1):
        if n not in have:
            rows.append(_unm(n, "no visit_%d folder" % n))
            prev = None
            continue
        t, why = _read(os.path.join(vd, "visit_%d" % n, "SUMMARY.md"))
        b = None if why else M.ingame_exit_block(t)
        if not why and b is None:
            why = "SUMMARY.md has no Exit block"
        if not why and not isinstance(b.get("ingame_rows"), dict):
            why = "the Exit block has no ingame_rows"
        if not why and not b["ingame_rows"]:
            why = "the Exit block's ingame_rows is empty"
        if why:
            rows.append(_unm(n, why))
            prev = None
            continue
        tr = b["ingame_rows"]
        so = b.get("strange_open") if _int(b.get("strange_open")) is not None else None
        cnt = {k: sum(1 for v in tr.values() if v == k) for k in ("pass", "fail", "unmeasured")}
        bad = {k for k, v in tr.items() if v != "pass"}
        r = {"round": n, "measured": so is not None, "pass": cnt["pass"], "fail": cnt["fail"],
             "unmeasured": cnt["unmeasured"], "strange_open": so, "exit_met": b.get("exit_met")}
        if so is None:
            r.update(why="the Exit block has no strange_open", new=None, fixed=None, open=None)
            prev = None
        else:
            r["open"] = len(bad) + so
            if prev is None:
                r["new"], r["fixed"] = len(bad) + so, None
            else:
                r["new"] = len(bad - prev[0]) + so
                r["fixed"] = sum(1 for k in prev[0] if tr.get(k) == "pass") + prev[1]
            prev = (bad, so)
        rows.append(r)
    return rows, None


# The word

def verdict(rows):
    """-> (word, why) on the measured rounds alone."""
    m = [r for r in rows if r.get("measured")]
    if not m:
        return UNM, "no measured round"
    if m[-1]["open"] == 0:
        return CONV, "nothing open"
    if len(m) < 2:
        return UNM, "one measured round"
    nw = [r["new"] for r in m[-3:]]
    if len(m) >= 3 and None not in nw and nw[0] <= nw[1] <= nw[2] and nw[2] > 0:
        return DIV, "new findings not falling over three rounds"
    if m[-1]["open"] > m[-2]["open"]:
        return DIV, "open rising"
    if m[-1]["open"] < m[-2]["open"]:
        return CONV, "open falling"
    return FLAT, "open unchanged"


def read_mod(d):
    out = {}
    for key, fn in (("3", stage3), ("4+5", stage45), ("6", stage6)):
        try:
            rows, why = fn(d)
        except Exception as e:      # noqa: BLE001  a record that breaks a reader reads UNMEASURED, never a crash
            rows, why = [], "reader failed: %s: %s" % (e.__class__.__name__, str(e)[:80])
        word, because = (UNM, why or "no round on file") if not rows else verdict(rows)
        out[key] = {"verdict": word, "because": because, "rounds": rows,
                    "missing": [r["round"] for r in rows if not r.get("measured")]}
    return out


def read_all(root=None):
    root = root or REPO
    cd = os.path.join(root, CONCEPTS)
    mods = {}
    for name in sorted(os.listdir(cd)) if os.path.isdir(cd) else []:
        if name.startswith((".", "_")) or not os.path.isdir(os.path.join(cd, name)):
            continue
        mods[name] = read_mod(os.path.join(cd, name))
    return {"source": SOURCE, "rule": "CONVERGING open falling or 0; FLAT open unchanged; DIVERGING open rising or new "
            "not falling over the last three rounds; UNMEASURED fewer than two measured rounds", "mods": mods}


def _seq(rows, key):
    return " -> ".join(str(r[key]) for r in rows if r.get("measured"))


def needs_lines(d):
    """-> one Needs Conductor line, with the numbers, per DIVERGING stage. It pauses nothing and changes no bar."""
    out = []
    names = dict(STAGES)
    for mod, st in sorted((d.get("mods") or {}).items()):
        for key, _ in STAGES:
            s = st.get(key) or {}
            if s.get("verdict") != DIV:
                continue
            rows = s.get("rounds") or []
            miss = " (unmeasured rounds %s)" % ", ".join(str(x) for x in s.get("missing")) if s.get("missing") else ""
            out.append("%s Stage %s (%s) DIVERGING, %s: open %s, new %s by measured round%s. Conductor decides; "
                       "this pauses nothing and changes no bar (%s)."
                       % (mod, key, names[key], s.get("because"), _seq(rows, "open"), _seq(rows, "new"), miss, SOURCE))
    return out


def annotate_reading(root, rd):
    """The Dispatch tick's hook: rd gets `convergence` {mod: {stage: {verdict, because, missing}}} and each DIVERGING
    line appended to rd['needs_conductor']. A failure here costs the tick nothing but this reading."""
    try:
        d = read_all(root)
    except Exception as e:      # noqa: BLE001
        rd["convergence_error"] = "%s: %s" % (e.__class__.__name__, str(e)[:120])
        return rd
    rd["convergence"] = {m: {k: {"verdict": s["verdict"], "because": s["because"], "missing": s["missing"],
                                 "open": [r["open"] for r in s["rounds"]], "new": [r["new"] for r in s["rounds"]]}
                             for k, s in st.items()} for m, st in d["mods"].items()}
    rd.setdefault("needs_conductor", []).extend(needs_lines(d))
    return rd


# The table (MATURATION_NOW's Convergence section)

def _cell(rows, key):
    """Round by round; a run of unmeasured rounds is one 'UNMEASURED xN'; '-' where a round has nothing to compare
    with (fixed on the first measured round, or after an unmeasured one)."""
    out = []
    for r in rows:
        if r.get("measured"):
            out.append("-" if r.get(key) is None else str(r[key]))
        elif out and out[-1].startswith(UNM):
            k = out[-1].split(" x")
            out[-1] = "%s x%d" % (UNM, (int(k[1]) if len(k) > 1 else 1) + 1)
        else:
            out.append(UNM)
    return ", ".join(out) or "-"


def table_rows(d):
    """-> [(mod, stage, word, open per round, new per round, fixed per round, rows text, because)] for every stage
    with a round on disk; a stage with no record at all is one UNMEASURED row per mod only when no stage has one."""
    out = []
    names = dict(STAGES)
    for mod, st in sorted((d.get("mods") or {}).items()):
        shown = False
        for key, _ in STAGES:
            s = st.get(key) or {}
            rows = s.get("rounds") or []
            if not rows:
                continue
            shown = True
            ig = ("; ".join("%s/%s/%s" % (r["pass"], r["fail"], r["unmeasured"]) if "pass" in r else UNM
                            for r in rows) if key == "6" else "")
            out.append((mod, "%s %s" % (key, names[key]), s["verdict"], _cell(rows, "open"), _cell(rows, "new"),
                        _cell(rows, "fixed"), ig, s.get("because") or ""))
        if not shown:
            out.append((mod, "-", UNM, "-", "-", "-", "", "no judging record on disk"))
    return out


HEAD = ("Mod", "Stage", "Word", "Open by round", "New by round", "Fixed by round", "In-game pass/fail/unmeasured", "Why")


def markdown(d):
    lines = ["| %s |" % " | ".join(HEAD), "|%s" % ("---|" * len(HEAD))]
    for r in table_rows(d):
        lines.append("| %s |" % " | ".join(str(x).replace("|", "/") for x in r))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=REPO)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--json", action="store_true", help="the full reading as JSON")
    g.add_argument("--print", action="store_true", help="the Markdown table (default)")
    a = ap.parse_args(argv)
    d = read_all(a.root)
    if a.json:
        print(json.dumps(d, indent=1, sort_keys=True))
    else:
        print("\n".join(markdown(d)))
        for ln in needs_lines(d):
            print("\nNeeds Conductor: " + ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
