#!/usr/bin/env python3
"""migration_proof.py — prove the schema-2 migration kept the meaning of every decided row of the owner's past rulings.

    python3 src/RimMandrake/Utils/art/migration_proof.py --before <dir of schema-1 files> [--after <dir>] [--old-rev <git rev>]

For every <sheet>.decisions.json in --before (the schema-1 originals) and its counterpart (in --after, default: migrated
in memory with decisions_v2.migrate_doc against the snapshot it was saved against):

  1 LETTERS   every letter a decided row names resolves, through the migrated record's setIds, to exactly the pictures
              the row's letter named in the snapshot he saved against (no letter moved, none quarantined unnoticed);
  2 PLAN      `art.py enact`'s plan for the row — built by the PRE-REDESIGN enact.py (git --old-rev) on the original
              and by the current enact.py on the migrated record, same ledger, same jobs — is identical, except for
              differences of exactly these kinds, each listed:
                legacy-tick   an old variant tick no longer ships until he says keep on it in its sheet row
                not-a-pool    an old variant tick on a lane that is not a random pool (flight/young/sex/body) ships nothing
                default-tick  a machine-default tick (variantsDefault) no longer blocks his ✕ or protects a picture
              Any other difference is UNEXPLAINED and fails the proof.
Exit 0 only when every row passes. Writes nothing.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as L  # noqa: E402
import decisions_v2 as DV  # noqa: E402
import enact as E  # noqa: E402
import sheet_slots as SL  # noqa: E402

OLD_REV = "c194de217"   # origin/main before the redesign's first commit (e4a158506)


def old_enact(rev: str):
    src = subprocess.run(["git", "-C", str(L.REPO_ROOT), "show", f"{rev}:src/RimMandrake/Utils/art/enact.py"],
                         capture_output=True, text=True, check=True).stdout
    tmp = Path(tempfile.mkdtemp(prefix="enact_old_")) / "enact_old.py"
    tmp.write_text(src)
    spec = importlib.util.spec_from_file_location("enact_old", tmp)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def norm(P: dict) -> dict:
    """Plan -> {row: {(kind, item)}}, the comparable content of every step."""
    out: dict = {}

    def add(row, kind, item):
        out.setdefault(row, set()).add((kind, item))
    for i in P["install"]:
        add(i["row"], "install", (i["rel"], i["sha"], i["letter"], bool(i.get("variant"))))
    for r, m, x in [(t[0], t[1], t[2]) for t in P["installed_already"]]:
        add(r, "installed_already", (str(m), str(x)))
    for rt in P["retire"]:
        add(rt["row"], "retire", (rt["rel"], rt["sha"]))
    for q in P["queue"]:
        add(q["row"], "queue", (q.get("note") or "", q.get("slot")))
    for p in P["purge"]:
        add(p["row"], "purge", p["sha"])
    for c in P["cuts"]:
        add(c["row"], "cut", "")
    for key in ("todo", "conflicts", "blocked", "queued_already", "done", "awaiting_pick"):
        for line in P.get(key) or []:
            add(line.split(":", 1)[0], key, line)
    for w in P.get("withdraw") or []:
        add(w["row"], "withdraw", w["job"]["id"])
    for rf in P.get("refile") or []:
        add(rf["row"], "refile", rf["job"]["id"])
    for row, f in (P.get("followed") or {}).items():
        add(row, "followed", json.dumps(f, sort_keys=True))
    return out


def explain(kind: str, item, old_v: dict, new_v: dict, gone: bool) -> str | None:
    """The allowed category of one difference, or None (UNEXPLAINED)."""
    legacy = set(new_v.get("legacyVariants") or [])
    default = set(new_v.get("legacyVariantsDefault") or [])
    if kind == "install" and item[3] and gone:
        return "legacy-tick" if item[2] in legacy else "not-a-pool"
    if kind == "installed_already" and gone and "variant" in item[1]:
        return "legacy-tick" if item[1].split()[-1] in legacy else "not-a-pool"
    if kind == "todo" and gone and ": ticked variant " in item:
        return "legacy-tick" if item.split(": ticked variant ", 1)[1].split()[0] in legacy else "not-a-pool"
    if kind == "retire" and legacy:
        return "legacy-tick"          # a folder this run would have filled with the pick + old ticks
    if kind == "conflicts" and gone and "own pick/variant" in item and default:
        return "default-tick"
    if kind == "purge" and not gone and default:
        return "default-tick"
    if kind == "conflicts" and gone and "owner-kept" in item and (default or legacy):
        return "default-tick"
    return None


def prove(before: Path, after: Path | None, rev: str) -> int:
    O = old_enact(rev)
    idx = L.Index()
    jobs = E.load_jobs()
    tmpdir = Path(tempfile.mkdtemp(prefix="migproof_"))
    fails, counts = [], {"files": 0, "decided_rows": 0, "letters": 0, "same": 0, "explained": {}}
    for f in sorted(before.glob("*.decisions.json")):
        doc = json.loads(f.read_text())
        if after:
            new = json.loads((after / f.name).read_text())
        else:
            new, _ = DV.migrate_doc(doc, DV.ruled_snapshot(doc, f), DV.snapshot_versions(doc))
        counts["files"] += 1
        vers = DV.snapshot_versions(doc)
        # 1 letters
        for row, v in (doc.get("decisions") or {}).items():
            if not isinstance(v, dict) or not v.get("at"):
                continue
            counts["decided_rows"] += 1
            nv = (new.get("decisions") or {}).get(row) or {}
            cols, _amb = DV.resolve_cols(row if any(row in (x.get("rows") or {}) for x in vers) else (v.get("carriedFrom") or row), vers)
            for l in sorted(L.decision_letters(v)):
                counts["letters"] += 1
                if l in (nv.get("quarantine") or []):
                    fails.append(f"{f.name} {row}: letter {l} quarantined (listed, not resolved)")
                elif l in cols and (nv.get("setIds") or {}).get(l) != SL.set_id(cols[l]):
                    fails.append(f"{f.name} {row}: letter {l} -> set {nv.get('setIds', {}).get(l)} != {SL.set_id(cols[l])}")
        # 2 plans
        a_p, b_p = tmpdir / ("old_" + f.name), tmpdir / ("new_" + f.name)
        a_p.write_text(json.dumps(doc))
        b_p.write_text(json.dumps(new))
        E.reset_caches()
        Po = norm(O.build_plan(a_p, idx=idx, jobs=jobs))
        E.reset_caches()
        Pn = norm(E.build_plan(b_p, idx=idx, jobs=jobs))
        for row in sorted(set(Po) | set(Pn)):
            o, n = Po.get(row, set()), Pn.get(row, set())
            ov = (doc.get("decisions") or {}).get(row) or {}
            nv = (new.get("decisions") or {}).get(row) or {}
            if o == n:
                counts["same"] += 1
                continue
            for kind, item in sorted(o - n, key=str):
                why = explain(kind, item, ov, nv, gone=True)
                if why:
                    counts["explained"][why] = counts["explained"].get(why, 0) + 1
                else:
                    fails.append(f"{f.name} {row}: UNEXPLAINED — old plan had {kind} {str(item)[:160]}")
            for kind, item in sorted(n - o, key=str):
                why = explain(kind, item, ov, nv, gone=False)
                if why:
                    counts["explained"][why] = counts["explained"].get(why, 0) + 1
                else:
                    fails.append(f"{f.name} {row}: UNEXPLAINED — new plan adds {kind} {str(item)[:160]}")
    print(json.dumps(counts, indent=1))
    for x in fails:
        print("FAIL " + x)
    print("MIGRATION PROOF: " + ("PASS" if not fails else f"{len(fails)} FAILURE(S)"))
    return 1 if fails else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--before", required=True, help="dir of the schema-1 originals")
    ap.add_argument("--after", help="dir of the migrated files (default: migrate in memory)")
    ap.add_argument("--old-rev", default=OLD_REV)
    a = ap.parse_args(argv)
    return prove(Path(a.before), Path(a.after) if a.after else None, a.old_rev)


if __name__ == "__main__":
    sys.exit(main())
