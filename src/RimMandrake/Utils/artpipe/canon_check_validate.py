#!/usr/bin/env python3
"""canon_check_validate.py — run canon_check v1 (stored verdicts) and v2 over an owner-labelled set; resumable.

    python3 canon_check_validate.py plan  [--keeps N] [--seed S]   write the frozen sample to <out>/set.json
    python3 canon_check_validate.py run   --split tune|held [--limit N] [-j N]   grade with v2, append to results.jsonl
    python3 canon_check_validate.py table                              confusion tables per split

Split is by SUBJECT (slug, else job-id stem) so near-duplicate renders never straddle tune/held. Rejects: tune
subjects are fixed below (chosen before any v2 run, <= half of the rejects); everything else is held-out.
v1 numbers are the verdicts already stored in each manifest (same code, same prompt family) — not re-spent."""
from __future__ import annotations
import argparse, hashlib, json, random, re, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import canon_check, canon_check_labelset, common  # noqa: E402

OUT = common.REPO_ROOT / "Transient" / "canon_check_v2"
TUNE_REJECT_SUBJECTS = {"eopie", "iriaz", "worrt", "skennet"}


def subject_of(x: dict) -> str:
    if x.get("slug"):
        return x["slug"]
    return re.sub(r"_(redo|master|v\d+|north|south|east|west|fly).*$", "", x["id"].replace("webwork_", ""))


def split_of(x: dict) -> str:
    sub = subject_of(x)
    if x["label"] == "reject":
        return "tune" if sub in TUNE_REJECT_SUBJECTS else "held"
    return "tune" if int(hashlib.md5(sub.encode()).hexdigest(), 16) % 2 == 0 else "held"


def plan(keeps: int, seed: int):
    OUT.mkdir(parents=True, exist_ok=True)
    allx = canon_check_labelset.build()
    for x in allx:
        x["subject"] = subject_of(x)
        x["split"] = split_of(x)
    rej = [x for x in allx if x["label"] == "reject"]
    kfail = [x for x in allx if x["label"] == "keep" and x["v1"] == "FAIL"]
    kpass = [x for x in allx if x["label"] == "keep" and x["v1"] == "PASS"]
    rnd = random.Random(seed)
    rest = max(0, keeps - len(kfail))
    # stratified: half canon-kind half owner-kind, one render per subject first so the sample is not one species
    pick = []
    for kind in ("canon", "owner"):
        pool = [x for x in kpass if x["kind"] == kind]
        rnd.shuffle(pool)
        seen, out = set(), []
        for x in pool:
            if x["subject"] not in seen:
                seen.add(x["subject"]); out.append(x)
        pick += out[: rest // 2]
    sel = rej + kfail + pick
    json.dump(sel, open(OUT / "set.json", "w"), indent=1)
    print(Counter((x["split"], x["label"], x["v1"]) for x in sel))


def run(split: str, limit: int | None, jobs: int, mode: str = "v2"):
    sel = [x for x in json.load(open(OUT / "set.json")) if x["split"] == split]
    resf = OUT / f"results_{mode}.jsonl"
    done = {json.loads(l)["id"] for l in resf.read_text().splitlines()} if resf.is_file() else set()
    todo = [x for x in sel if x["id"] not in done][: limit or None]
    def one(x):
        job = json.loads((common.DEFAULT_DONE / f"{x['id']}.json").read_text())
        spec = canon_check.gather(job)
        png = common.DEFAULT_ARTSRC / x["id"] / f"{x['id']}.png"
        try:
            r = canon_check.grade(png, spec, mode=mode)
            return {"id": x["id"], "verdict": r["verdict"], "score": r["score"], "gate_failed": r.get("gate_failed"),
                    "fails": [l["line"][:90] + " :: " + l["reason"][:140] for l in r["lines"] if l["verdict"] == "fail"],
                    "descr": r.get("descriptions")}
        except Exception as exc:  # noqa: BLE001
            return {"id": x["id"], "error": f"{type(exc).__name__}: {exc}"[:300]}
    with ThreadPoolExecutor(max_workers=jobs) as ex, open(resf, "a") as f:
        for rec in ex.map(one, todo):
            f.write(json.dumps(rec) + "\n"); f.flush()
            print(rec["id"], rec.get("verdict") or rec.get("error"), flush=True)


def table():
    sel = {x["id"]: x for x in json.load(open(OUT / "set.json"))}
    v2 = {}
    p = OUT / "results_v2.jsonl"
    if p.is_file():
        for l in p.read_text().splitlines():
            r = json.loads(l); v2[r["id"]] = r
    for split in ("tune", "held", "all"):
        for ver in ("v1", "v2"):
            c = Counter(); err = 0
            for x in sel.values():
                if split != "all" and x["split"] != split:
                    continue
                if ver == "v1":
                    v = x["v1"]
                else:
                    r = v2.get(x["id"])
                    if r is None:
                        continue
                    if "error" in r:
                        err += 1; continue
                    v = r["verdict"]
                c[(x["label"], v)] += 1
            rj, kp = c[("reject", "PASS")], c[("keep", "FAIL")]
            nr, nk = c[("reject", "PASS")] + c[("reject", "FAIL")], c[("keep", "PASS")] + c[("keep", "FAIL")]
            print(f"{split:5} {ver}: rejects caught {c[('reject','FAIL')]}/{nr}  keeps wrongly failed {kp}/{nk}  errors {err}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "run", "table"])
    ap.add_argument("--keeps", type=int, default=37); ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--split"); ap.add_argument("--limit", type=int); ap.add_argument("-j", type=int, default=2)
    ap.add_argument("--mode", default="v2")
    a = ap.parse_args()
    {"plan": lambda: plan(a.keeps, a.seed), "run": lambda: run(a.split, a.limit, a.j, a.mode), "table": table}[a.cmd]()
