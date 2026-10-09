#!/usr/bin/env python3
"""render_subjects.py — the DERIVED subject index for historic renders (ART_SUBJECT_RESOLVER_1 §5.3).

    python3 render_subjects.py [--out PATH] [--write-bindings]   (default: build + report, writes only the index)

For every artpipe render variant in the art ledger, resolve which subject (defName) it is a picture of, by the
spec's order, never mutating a job file in the artpipe state dir:
  1 bound        a ledger `binding` event (the job's target_def) — or collected.jsonl installed it at a texPath
  1 bound        byte join: the render's sha is, or its dHash (<= NEAR bits) equals, a non-artpipe ledger variant
                 of a texPath (installed by hand; the bytes prove it)
  3 name-matched whole-token match of the job family to exactly ONE candidate subject
  ambiguous      two or more candidate subjects: listed, never guessed
  unresolved     nothing
Step 2 (owner rulings -> sha) has nothing to read: every imported ruling is legacy-unresolved and names no bytes.
Output: <ledger dir>/render_subjects.json (gitignored, regenerable). `--write-bindings` appends the bound and
name-matched results to the art ledger as idempotent `binding` events (deterministic ids), the only ledger write.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import subject as S  # noqa: E402

NEAR = 10


def candidates(w: "S.World") -> dict:
    """key -> set of candidate GROUPS (our defNames sharing a texPath set collapse to one group, named by sorted defNames).
    An exact stem key outranks a variant-stripped key."""
    exact, stripped = defaultdict(set), defaultdict(set)
    tbd = w.tex_by_def
    for dn, rec in w.defs.items():
        if not S.OURS_RE.match(dn):
            continue
        st = S.norm(S.stem(dn))
        if len(st) >= S.MIN_KEY:
            exact[st].add(dn)
        v = S.variant_stripped(dn)
        if len(v) >= S.MIN_KEY:
            stripped[v].add(dn)
        for j in S.join_stems(dn)[1:]:
            if len(S.norm(j)) >= S.MIN_KEY:
                exact[S.norm(j)].add(dn)
        lab = S.norm(rec.get("label") or "")
        if len(lab) >= S.MIN_KEY:
            exact[lab].add(dn)

    def groups(dns):
        g = {}
        for dn in dns:
            tp = frozenset(tbd.get(dn, ()))
            g.setdefault(tp or dn, set()).add(dn)
        return [sorted(v) for v in g.values()]
    return {"exact": {k: groups(v) for k, v in exact.items()}, "stripped": {k: groups(v) for k, v in stripped.items()}}


def build(w: "S.World | None" = None, idx: "L.Index | None" = None) -> dict:
    w = w or S.World()
    idx = idx or L.Index()
    cand = candidates(w)
    # non-artpipe variants of a texPath: the byte-join targets
    by_sha, by_ph = {}, defaultdict(list)
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("res") and v.get("kind") != "artpipe":
                by_sha.setdefault(sha, v["res"])
                if v.get("ph"):
                    by_ph[v["ph"]].append(v["res"])
    near_pool = [(int(ph, 16), res) for ph, rs in by_ph.items() for res in rs[:1]]
    dbt = w.def_by_tex
    only_defs = lambda tps: sorted({d for tp in tps for d in dbt.get(tp, ())})
    out, tally = {}, Counter()
    for sha, vs in idx.variants.items():
        for v in vs:
            if v.get("kind") != "artpipe" or not v.get("job") or idx.is_purged(sha):
                continue
            job = v["job"]
            fam = S.FAM_RE.sub("", job)
            rec = {"job": job, "family": fam}
            bd = [b for b in idx.bindings.get(sha, []) if b.get("job") == job]
            if bd:
                rec.update(resolution="bound", via="binding", subjects=sorted({b["subject"] for b in bd}),
                           evidence=bd[0]["evidence"])
            elif w.collected.get(job) and dbt.get(w.collected[job]):
                rec.update(resolution="bound", via="collected", subjects=sorted(dbt[w.collected[job]]), texpath=w.collected[job],
                           evidence=f"collected.jsonl installed it at {w.collected[job]}")
            elif sha in by_sha:
                res = by_sha[sha]
                rec.update(resolution="bound", via="byte-join", subjects=only_defs([res]), texpath=res,
                           evidence=f"sha equals a ledger variant of texPath {res}")
            else:
                rec["resolution"] = None
            if rec["resolution"] is None and v.get("ph"):
                n = int(v["ph"], 16)
                hit = next((res for (m, res) in near_pool if bin(n ^ m).count("1") <= NEAR), None)
                if hit:
                    rec.update(resolution="bound", via="dhash-join", subjects=only_defs([hit]), texpath=hit,
                               evidence=f"dHash within {NEAR} bits of a ledger variant of texPath {hit}")
            if rec["resolution"] is None:
                found = {}
                for tier in ("exact", "stripped"):
                    for k, gs in cand[tier].items():
                        if S.token_match(fam, k):
                            for g in gs:
                                found[tuple(g)] = k
                    if found:
                        break
                if len(found) == 1:
                    (g, k), = found.items()
                    rec.update(resolution="name-matched", via="token", subjects=list(g),
                               evidence=f"job id token {k!r}")
                elif found:
                    rec.update(resolution="ambiguous", via="token", subjects=sorted({d for g in found for d in g}),
                               evidence=f"{len(found)} candidate subject groups: " + "; ".join(sorted(found.values())))
                else:
                    rec.update(resolution="unresolved", via=None, subjects=[], evidence="no binding, join or token match")
            out[f"{sha}:{job}"] = rec
            tally[rec["resolution"] + (f"/{rec['via']}" if rec["via"] else "")] += 1
    return {"tally": dict(sorted(tally.items())), "renders": len(out), "entries": out}


def write_bindings(res: dict) -> int:
    w = L.Writer()
    n0 = len(w.known)
    for key, r in res["entries"].items():
        if r["via"] == "binding" or r["resolution"] not in ("bound", "name-matched") or len(r["subjects"]) != 1:
            continue
        sha, job = key.split(":", 1)
        w.add({"type": "binding", "id": L.det_id("binding", "derived", sha, job, r["subjects"][0]), "sha": sha, "job": job,
               "subject": r["subjects"][0], "originals": [], "texpath": r.get("texpath"), "confidence": r["resolution"],
               "evidence": r["evidence"]})
    w.flush()
    return len(w.known) - n0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--write-bindings", action="store_true")
    a = ap.parse_args(argv)
    res = build()
    p = Path(a.out) if a.out else L.ledger_dir() / "render_subjects.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(res, indent=0, sort_keys=True))
    print(json.dumps({"renders": res["renders"], "tally": res["tally"], "index": str(p)}, indent=1))
    if a.write_bindings:
        print("binding events written:", write_bindings(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
