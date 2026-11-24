#!/usr/bin/env python3
"""vv_laws.py - the written conservation laws and sanity principles the shipped-settings fuzz matrix enforces
(RIMMANDRAKE_REVIVE_SHIPPED_FUZZ_WITH_LAWS; owner 2026-11-12: "offline randomized validation scripts with sanity checks
and conservation laws/principles outlined that must be obeyed. Keep it in please. Especially since it's offline.").

    python3 src/RimMandrake/Utils/vv_laws.py lint                  offline, no build: every law is checkable
    python3 src/RimMandrake/Utils/vv_laws.py prove [Mod] [--family F] [--out record.json]
                                                                  each law family goes red under its planted break
    python3 src/RimMandrake/Utils/vv_laws.py name <rates.jsonl>    which laws a matrix run's red families broke

`lint` checks references and plant definitions (texts present, a plant that changes something); only `prove` shows a
family can actually go red. The laws live beside each mod's kernel, one JSON per mod (LAW_FILES): a law is an id, a plain sentence, the matrix family
that checks it and the EXACT assertion text in source ({...} placeholders match anything). A law family names its
planted break: `hook` (ShippedMatrixProbe --plant: state corrupted at the moment the shipped settings are written),
`source` (one find/replace in the STAGED copy of a kernel file) or `mutation` (a named defect of
mutate_empirepursuit_fuzz.py). `prove` runs, per family, an unplanted baseline (must be green: else the red proves
nothing) and the planted run (must be red, with a failure naming one of THAT family's laws: a red from another law is
recorded as such, never counted). vv_shipped_matrix.py refuses to run when `lint` finds a problem and names the broken
laws of any family red at the shipped settings.

Exit codes: lint 0 clean / 1 problems · prove 0 every family proven / 1 a family not proven (named) / 2 could not run.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
LAW_FILES = {
    "FlowWorks": "src/RimMandrake/FlowWorks/Source/SelfTest/VV/laws.json",
    "EmpirePursuit": "src/RimUtinni/EmpirePursuit/Source/SelfTest/VV/laws.json",
}
PROBE = "src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs"
HOOK_PLANTS = ("volume", "bounds", "shuttle")
ID_RE = re.compile(r"^[a-z][a-z0-9_]{5,63}$")
PROVE_N = {"kernel_fuzz": 300, "seq_orders": 3000, "seq_conversion": 300, "seq_sequences": 300, "seq_pitwidth": 300,
           "fills_from_limitless": 300, "surface_random": 300}
# A law family that applies to few generated scenes proves on more: `settling` judges only a sinkless scene of 100+
# pulses whose bodies are spent and gave nothing in the window: 58 of 10,000 kernel_fuzz scenes, 14 of them holding
# water, and its shuttle plant red in 13 [measured 2026-11-18, RIMMANDRAKE_PLANT_FLOWWORKS_SETTLING_LAW_SHUTTLE_TRIPS_OTHERS]:
# at 300 scenes that plant would be red about 0.4 times.
PROVE_N_FAMILY = {"settling": {"kernel_fuzz": 10000}}


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def load(mod, root=None):
    with open(os.path.join(root or ROOT, LAW_FILES[mod]), encoding="utf-8") as f:
        return json.load(f)


def matrix_families(mod):
    """The families the matrix runs for a mod (vv_shipped_matrix.SHIPPED_N / EP_N), without importing its build deps."""
    t = _read("src/RimMandrake/Utils/vv_shipped_matrix.py")
    name = "SHIPPED_N" if mod == "FlowWorks" else "EP_N"
    m = re.search(r"^%s = \{([^}]*)\}" % name, t, re.M)
    return re.findall(r'"(\w+)":', m.group(1)) if m else []


def mutation_names():
    t = _read("src/RimMandrake/Utils/mutate_empirepursuit_fuzz.py")
    return set(re.findall(r'^\s*\("([^"]+)",', t, re.M))


def text_re(text):
    """An assertion text with {placeholders} -> a regex over a failure message."""
    parts = re.split(r"\{[^{}]*\}", text)
    return re.compile(".*?".join(re.escape(p) for p in parts), re.S)


def lint(doc, read=_read, fams=None, mutations=None):
    """-> problems (strings). Empty = every law is checkable and every family can be shown to go red."""
    p, seen = [], set()
    mod = doc.get("mod")
    fams = matrix_families(mod) if fams is None else fams
    families = doc.get("families") or {}
    laws = doc.get("laws") or []
    if not laws:
        p.append("%s: no laws" % mod)
    for law in laws:
        lid = law.get("id") or ""
        if not ID_RE.match(lid):
            p.append("%s: law id %r is not a lower_snake name" % (mod, lid))
        if lid in seen:
            p.append("%s: law %s declared twice" % (mod, lid))
        seen.add(lid)
        if not (law.get("sentence") or "").strip():
            p.append("%s: law %s has no sentence" % (mod, lid))
        if law.get("family") not in families:
            p.append("%s: law %s's family %r declares no planted break" % (mod, lid, law.get("family")))
        if law.get("matrix_family") not in fams:
            p.append("%s: law %s's matrix family %r is not run by the matrix (%s)" % (mod, lid, law.get("matrix_family"), ", ".join(fams)))
        ck = law.get("check") or {}
        try:
            src = read(ck.get("file") or "")
        except OSError:
            p.append("%s: law %s's check file %s cannot be read" % (mod, lid, ck.get("file")))
            continue
        if not ck.get("text") or ck["text"] not in src:
            p.append("%s: law %s's assertion text %r is not in %s (the check moved or was reworded)" % (mod, lid, ck.get("text"), ck.get("file")))
    for name, fam in families.items():
        pl = (fam or {}).get("plant") or {}
        if not any(l.get("family") == name for l in laws):
            p.append("%s: family %s has no law" % (mod, name))
        kind = pl.get("kind")
        if kind == "hook":
            if pl.get("name") not in HOOK_PLANTS or ('"%s"' % pl.get("name")) not in read(PROBE):
                p.append("%s: family %s's hook plant %r is not one ShippedMatrixProbe knows" % (mod, name, pl.get("name")))
        elif kind == "source":
            try:
                n = read(pl.get("file") or "").count(pl.get("find") or "\0")
            except OSError:
                n = -1
            if n != 1 or not pl.get("find"):
                p.append("%s: family %s's source plant is found %s time(s) in %s (want exactly 1)" % (mod, name, n, pl.get("file")))
            if "replace" not in pl or pl.get("replace") == pl.get("find"):
                p.append("%s: family %s's source plant changes nothing (replacement missing or equal to its find)" % (mod, name))
        elif kind == "mutation":
            names = mutation_names() if mutations is None else mutations
            if pl.get("name") not in names:
                p.append("%s: family %s's mutation %r is not in mutate_empirepursuit_fuzz.py" % (mod, name, pl.get("name")))
        else:
            p.append("%s: family %s has no planted break (kind %r)" % (mod, name, kind))
    return p


def lint_all():
    out = []
    for mod in LAW_FILES:
        try:
            out += lint(load(mod))
        except (OSError, ValueError) as ex:
            out.append("%s: law file %s unreadable: %s" % (mod, LAW_FILES[mod], ex))
    return out


def uncovered(mod):
    doc = load(mod)
    have = {l["matrix_family"] for l in doc["laws"]}
    return [f for f in matrix_families(mod) if f not in have]


def name_failures(rec, docs=None):
    """The law ids a matrix rates record's failure examples name. [] = looked, none named; the caller says so."""
    fam = rec.get("family") or ""
    mod, mf = ("EmpirePursuit", fam[3:]) if fam.startswith("ep_") else ("FlowWorks", fam)
    try:
        doc = (docs or {}).get(mod) or load(mod)
    except (OSError, ValueError):
        return ["(law file of %s unreadable)" % mod]
    exs = rec.get("examples") or []       # one message at a time: two unrelated messages never make one law's text
    return sorted(l["id"] for l in doc["laws"] if l["matrix_family"] == mf and any(text_re(l["check"]["text"]).search(e) for e in exs))


# ------------------------------------------------------------------ prove

def _family_laws(doc, name):
    return [l for l in doc["laws"] if l["family"] == name]


def judge(doc, name, baseline, planted):
    """-> (status, why). baseline/planted: the rates records of the family's matrix family (lists). PROVEN needs a green
    baseline and a red planted run naming one of this family's laws."""
    if not baseline or not planted:
        return "UNMEASURED", "a run wrote no record"
    b, p = baseline[-1], planted[-1]
    for who, r in (("baseline", b), ("planted run", p)):
        if not isinstance(r.get("completed"), int) or r["completed"] <= 0 or not isinstance(r.get("failures"), int):
            return "UNMEASURED", "the %s completed no case (record %s): zero work proves nothing" % (who, {k: r.get(k) for k in ("completed", "failures")})
    if b.get("timed_out") or p.get("timed_out") or b.get("unmeasured") or p.get("unmeasured"):
        return "UNMEASURED", "a run timed out or could not measure"
    if b.get("failures") or b.get("exceptions"):
        return "NOT_PROVEN", "the unplanted baseline is already red (%s/%s): the plant proves nothing" % (b.get("failures"), b.get("completed"))
    if not p.get("failures"):
        return "NOT_PROVEN", "the planted break stayed green (%s/%s, planted %s): the laws cannot see it" % (
            p.get("failures"), p.get("completed"), p.get("planted"))
    mine = {l["id"] for l in _family_laws(doc, name)}
    named = set(name_failures(p, {doc["mod"]: doc}))
    if named & mine:
        return "PROVEN", "red %s/%s by %s" % (p["failures"], p["completed"], ", ".join(sorted(named & mine)))
    return "NOT_PROVEN", "red %s/%s, but by %s, not by this family's laws" % (
        p["failures"], p["completed"], ", ".join(sorted(named)) or "no named law (examples: %s)" % (p.get("examples") or ["-"])[0])


def prove_flowworks(doc, only=None, log=print):
    import vv_shipped_matrix as M
    d = M.derive()
    shipped = d["shipped"]
    results, built = {}, {}
    run_dir = os.path.join(M.STAGE + "_laws", time.strftime("%Y%m%dT%H%M%S"))
    os.makedirs(run_dir, exist_ok=True)
    for name, fam in doc["families"].items():
        if only and name != only:
            continue
        pl = fam["plant"]
        mfs = sorted({l["matrix_family"] for l in _family_laws(doc, name)})
        tag = "" if pl["kind"] == "hook" else name
        if tag not in built:
            plants = [(pl["file"], pl["find"], pl["replace"])] if pl["kind"] == "source" else []
            built[tag] = M.stage_flowworks(source_plants=plants, tag=tag)
            if tag and "" not in built:
                built[""] = M.stage_flowworks()
        for mf in mfs:
            n = {mf: PROVE_N_FAMILY.get(name, {}).get(mf, PROVE_N.get(mf, 300))}
            base_out, plant_out = os.path.join(run_dir, "%s_%s_base.jsonl" % (name, mf)), os.path.join(run_dir, "%s_%s_plant.jsonl" % (name, mf))
            M.rates(built[""], base_out, "LAWS_BASELINE", shipped, n, 600, 1)
            M.rates(built[tag], plant_out, "LAWS_PLANT_" + name, shipped, n, 600, 1, plant=pl["name"] if pl["kind"] == "hook" else None)
            rd = lambda p: [json.loads(x) for x in open(p)] if os.path.exists(p) else []  # noqa: E731
            st, why = judge(doc, name, rd(base_out), rd(plant_out))
            results["%s/%s" % (name, mf)] = {"status": st, "why": why, "plant": pl}
            log("  %-34s %-11s %s" % ("%s/%s" % (name, mf), st, why))
    return results, run_dir


def prove_ep(doc, only=None, log=print):
    results = {}
    for name, fam in doc["families"].items():
        if only and name != only:
            continue
        pl = fam["plant"]
        # only the fuzz family the laws are checked by: ladder runs first and a mutation run prints one FAIL line
        mfs = sorted({l["matrix_family"] for l in _family_laws(doc, name)})
        fuzz_only = ["--fuzz-only", mfs[0]] if len(mfs) == 1 else []
        try:
            r = subprocess.run([sys.executable, os.path.join(HERE, "mutate_empirepursuit_fuzz.py"), pl["name"]] + fuzz_only, cwd=ROOT,
                               capture_output=True, text=True, timeout=3600)
        except (subprocess.TimeoutExpired, OSError) as ex:
            results[name] = {"status": "UNMEASURED", "why": "the mutation run timed out or could not start: %s" % type(ex).__name__, "plant": pl}
            log("  %-34s %-11s %s" % (name, "UNMEASURED", results[name]["why"]))
            continue
        out = (r.stdout or "") + (r.stderr or "")
        mine = [l for l in _family_laws(doc, name) if text_re(l["check"]["text"]).search(out)]
        if r.returncode == 0 and mine:
            st, why = "PROVEN", "caught by %s" % ", ".join(l["id"] for l in mine)
        elif r.returncode == 0:
            st, why = "NOT_PROVEN", "the fuzz caught the mutation, but no failure text of this family's laws shows (output: %s)" % out.strip()
        elif "SURVIVED" in out or "survived" in out:
            st, why = "NOT_PROVEN", "the mutation survived: the fuzz stayed green (output: %s)" % out.strip()
        else:
            st, why = "UNMEASURED", "mutate_empirepursuit_fuzz.py exited %d (output: %s)" % (r.returncode, out.strip())
        results[name] = {"status": st, "why": why, "plant": pl}
        log("  %-34s %-11s %s" % (name, st, why))
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lint")
    pr = sub.add_parser("prove")
    pr.add_argument("mod", nargs="?", choices=sorted(LAW_FILES))
    pr.add_argument("--family")
    pr.add_argument("--out")
    nm = sub.add_parser("name")
    nm.add_argument("rates")
    a = ap.parse_args(argv)
    if a.cmd == "lint":
        probs = lint_all()
        if probs:                                      # print the problems before any summary could trip on the same file
            for x in probs:
                print("PROBLEM", x)
            print("laws: %d problem(s)" % len(probs))
            return 1
        for mod in LAW_FILES:
            doc = load(mod)
            print("%s: %d laws in %d families; matrix families with no law yet: %s" % (
                mod, len(doc["laws"]), len(doc["families"]), ", ".join(uncovered(mod)) or "none"))
        for x in probs:
            print("PROBLEM", x)
        print("laws: %s" % ("every law checkable" if not probs else "%d problem(s)" % len(probs)))
        return 1 if probs else 0
    if a.cmd == "name":
        for line in open(a.rates, encoding="utf-8"):
            r = json.loads(line)
            if r.get("failures"):
                print("%-28s %-30s %d/%d laws: %s" % (r["config"], r["family"], r["failures"], r["completed"], ", ".join(name_failures(r)) or "none named"))
        return 0
    probs = lint_all()
    if probs:
        print("could not prove: the law lists have problems: " + "; ".join(probs))
        return 2
    record = {"when": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "results": {}}
    try:
        for mod in ([a.mod] if a.mod else sorted(LAW_FILES)):
            doc = load(mod)
            print("== %s ==" % mod)
            if mod == "FlowWorks":
                res, run_dir = prove_flowworks(doc, a.family)
                record["flowworks_run_dir"] = run_dir
            else:
                res = prove_ep(doc, a.family)
            record["results"][mod] = res
    except SystemExit as ex:                           # vv_shipped_matrix exits on a build failure: could not run
        print("could not prove: %s" % ex)
        return 2
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=1)
    st = [r["status"] for m in record["results"].values() for r in m.values()]
    print("laws proven: %d of %d family checks%s" % (st.count("PROVEN"), len(st), "" if all(s == "PROVEN" for s in st) else
                                                       " (NOT_PROVEN %d, UNMEASURED %d)" % (st.count("NOT_PROVEN"), st.count("UNMEASURED"))))
    if not st:
        return 2
    if "UNMEASURED" in st and "NOT_PROVEN" not in st:
        return 2
    return 0 if all(s == "PROVEN" for s in st) else 1


if __name__ == "__main__":
    sys.exit(main())
