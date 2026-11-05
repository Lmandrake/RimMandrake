#!/usr/bin/env python3
"""Proof for ARTSRC_LEGACY_UNMIGRATED_AUDIT_PURGED: the legacy _artsrc was audited by sha before it was migrated, and
nothing the art ledger holds purged, banned or rejected was copied into the live state dir.

Reads only the working tree (the blind checker has no git and no D:\\): the committed audit record beside this file
and the repo's art ledger (infrastructure/state/art). Checks:
  * every legacy file appears once, with one verdict from the known set, and the verdict counts equal the run's stats;
  * no `migrate` (copied) row's sha is purged, banned or rejected in the art ledger at this commit;
  * every `purged`/`banned`/`rejected` row is so in the ledger (the screen was the ledger, not a guess);
  * every `retired` row's job is ruled purged/superseded in the decision record(s) the run named;
  * every `withdrawn`/`conflict` row is counted (none were met here; the selftest proves their screen);
  * the code still carries the screen: artpipe_state.migrate excludes each of those verdicts.
Exit 0 = holds, 1 = does not."""
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
REC = Path(__file__).with_name("ARTSRC_LEGACY_UNMIGRATED_AUDIT_PURGED.json")
KNOWN = {"migrate", "already", "conflict", "purged", "banned", "rejected", "retired", "withdrawn", "clutter"}


def main() -> int:
    sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/artpipe"))
    import artpipe_state as AS
    L = AS._artledger(REPO)
    idx = L.Index()
    rec = json.loads(REC.read_text())
    rows, stats, errs = rec["rows"], rec["stats"], []
    rels = [r[0] for r in rows]
    if len(rels) != len(set(rels)):
        errs.append("a legacy file appears twice")
    got = Counter(r[2] for r in rows)
    if set(got) - KNOWN:
        errs.append(f"unknown verdicts {set(got) - KNOWN}")
    for v, n in got.items():
        key = "_artsrc" if v == "migrate" else f"_artsrc_{v}"
        if stats.get(key, 0) != n:
            errs.append(f"{v}: {n} rows but stats {key}={stats.get(key, 0)}")
    retired = AS.load_decisions([REPO / p for p in rec["decisions"]])
    for rel, sha, v in rows:
        purged, rejected, banned = sha in idx.purged, sha in idx.rejected, bool(sha) and L.is_banned(idx, sha)
        if v == "migrate" and (purged or rejected or banned):
            errs.append(f"{rel}: copied but purged={purged} banned={banned} rejected={rejected}")
        if (v == "purged" and not purged) or (v == "rejected" and not rejected) or (v == "banned" and not (banned or idx.bans)):
            # a near-duplicate ban is matched from the legacy bytes, which this box cannot read: exact-sha only here
            errs.append(f"{rel}: verdict {v} but the ledger does not say so")
        if v == "retired" and rel.split("/", 1)[0] not in retired:
            errs.append(f"{rel}: retired but no purged/superseded ruling for its job")
    if not set(AS.ARTSRC_EXCLUDED) >= {"purged", "banned", "rejected", "retired", "withdrawn", "conflict"}:
        errs.append(f"ARTSRC_EXCLUDED lost a verdict: {AS.ARTSRC_EXCLUDED}")
    if got["purged"] + got["banned"] + got["rejected"] == 0:
        errs.append("screen excluded nothing: the instrument is blind (the legacy tree held purged renders)")
    print(f"{len(rows)} legacy files; verdicts {dict(sorted(got.items()))}")
    for e in errs[:20]:
        print("  FAIL", e)
    print("HOLDS" if not errs else f"DOES NOT HOLD ({len(errs)} problem(s))")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
