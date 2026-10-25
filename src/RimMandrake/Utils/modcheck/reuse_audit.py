"""modcheck.reuse_audit -- classify a run's stale-hash UNMEASURED rows by what reuse could do for them (option B).

    python3 src/RimMandrake/Utils/modcheck/reuse_audit.py <run.json> [--mod-dir src/RimMandrake/FlowWorks] [--out FILE]

A FlowWorks reader row (core_live_rows, hose_live_rows, a driver_rows_at chain) that found no result "at the current
mod hash" is one of four kinds:
  never measured   no live result on disk carries the row at all: only a live run can answer it
  no manifest      results carry it, none stamped a run manifest (written before 2026-10-25): re-run once, then reusable
  relevant change  a manifested result carries it, but runtime / test closure / DLL differ: a re-run is owed
  reusable         a manifested result still matches (modcheck/reuse.py why_not is None): `run --reuse on` takes it
The row ids come from the run's components; a bar component (validation.DRIVER_BAR_ROWS) is judged on the driver rows it
reads. Result patterns are read from validation.py's literals (DRIVER_RESULTS, DRIVER_BAR_ROWS) by ast: nothing is imported
from the mod. Offline, read-only.
"""
import argparse
import ast
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import reuse  # noqa: E402

STALE = "at the current mod hash"
FIXED = {"core_live_rows": (("validation_v2_result_*.json",), False),
         "hose_live_rows": (("proof_hose_*.json",), True)}
CLASSES = ("never measured", "no manifest", "relevant change", "reusable")


def _literal(path, name):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            try:
                return ast.literal_eval(node.value)
            except ValueError:
                return None
    return None


def _repo_dll_sha(mod_dir):
    import hashlib
    for p in sorted(glob.glob(os.path.join(mod_dir, "Assemblies", "*.dll"))):
        if os.path.basename(p).startswith("RimMandrake"):
            with open(p, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
    return None


def _results(ns, patterns, certifiable):
    out = []
    for g in patterns:
        for p in sorted(glob.glob(os.path.join(ns, g))):
            d = reuse._load(p)
            if d and d.get("mode") == "live" and not d.get("aborted") and (d.get("certifiable") or not certifiable):
                out.append((p, d, {r.get("id") for r in d.get("rows") or []}))
    return out


def classify(ids, results, mod_dir, dll_sha, certifiable, _why=None):
    """(class, detail) for a row read from driver rows `ids` among `results` [(path, d, row id set)]. Pure given _why."""
    why_not = _why or (lambda d: reuse.why_not(d, mod_dir, dll_sha, certifiable))
    carry = [(p, d) for p, d, have in results if have & set(ids)]
    if not carry:
        return "never measured", "no live result carries %s" % ",".join(ids)[:120]
    reasons, cover, used = [], set(), []
    for p, d, have in results:
        if not have & set(ids):
            continue
        w = why_not(d)
        if w is None:
            cover |= have
            used.append(os.path.basename(p))
        elif isinstance(d.get("manifest"), dict):
            reasons.append("%s: %s" % (os.path.basename(p), w))
    if set(ids) <= cover:              # the reader needs EVERY id (a bar reads several rows), possibly across results
        return "reusable", ",".join(used)[:200]
    if used:
        reasons.append("reusable results carry only %s of %s" % (",".join(sorted(cover & set(ids))), ",".join(ids)))
    if reasons:
        return "relevant change", reasons[-1][:200]
    return "no manifest", "%d results carry it, newest %s" % (len(carry), os.path.basename(carry[-1][0]))


def audit(run, mod_dir):
    ns = os.path.join(mod_dir, "northstar")
    vpath = os.path.join(mod_dir, "validation.py")
    driver = tuple(_literal(vpath, "DRIVER_RESULTS") or ())
    bars = _literal(vpath, "DRIVER_BAR_ROWS") or {}
    dll = _repo_dll_sha(mod_dir)
    cache = {}
    rows = []
    chains = (run.get("summary") or run).get("chains") or []
    for ch in chains:
        for c in ch.get("components") or []:
            if c.get("verdict") != "UNMEASURED" or STALE not in str(c.get("detail") or ""):
                continue
            pats, cert = FIXED.get(ch["name"], (driver, False))
            key = (pats, cert)
            if key not in cache:
                cache[key] = _results(ns, pats, cert)
            ids = [c["name"]]
            for b in c.get("shows") or []:
                if b in bars:
                    ids = list(bars[b][0])
            cls, det = classify(ids, cache[key], mod_dir, dll, cert)
            rows.append({"chain": ch["name"], "row": c["name"], "class": cls, "detail": det})
    return rows


def report(rows):
    by = collections.Counter(r["class"] for r in rows)
    out = ["%d stale-hash UNMEASURED rows" % len(rows)]
    out += ["  %-16s %d" % (k, by.get(k, 0)) for k in CLASSES]
    per = collections.defaultdict(collections.Counter)
    for r in rows:
        per[r["chain"]][r["class"]] += 1
    out.append("per chain:")
    for ch, cnt in sorted(per.items(), key=lambda kv: -sum(kv[1].values())):
        out.append("  %-34s %s" % (ch, ", ".join("%s=%d" % (k, cnt[k]) for k in CLASSES if cnt[k])))
    out.append("rows:")
    out += ["  %s/%s: %s -- %s" % (r["chain"], r["row"], r["class"], r["detail"]) for r in rows]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run")
    ap.add_argument("--mod-dir", default=os.path.join(os.path.dirname(os.path.dirname(HERE)), "FlowWorks"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    with open(a.run, encoding="utf-8") as f:
        run = json.load(f)
    lines = report(audit(run, a.mod_dir))
    text = "\n".join(lines) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("\n".join(lines[:8 + len(CLASSES)]))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
