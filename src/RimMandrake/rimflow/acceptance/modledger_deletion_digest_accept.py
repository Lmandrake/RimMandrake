#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_LIST_MODLEDGER_DELETIONS_ON_DAILY_DIGEST (his ruling 2026-11-15 ~10:16 PM PST, via
the Conductor: "Delete on sight. I really don't think that's going to be abused to pass a judge. But we can monitor.";
design/specs/2026-11-15-mod-ledger-entry-standard.md §3 and build step 13). Written by the filing seat; the builder
does not edit it (a wrong clause goes to the Conductor).

    python3 src/RimMandrake/rimflow/acceptance/modledger_deletion_digest_accept.py      # "PASS 6/6" when built

THE CONTRACT. `modledger.deletions(root, since)` (built, 2026-11-15) is the monitor; this item puts its `flagged` rows
on the Conductor's daily digest, through the digest's blind contract:
  - "deletion" is a source in contracts.blind.SOURCES and in delegated_digest.SOURCES (and LATER_SOURCES);
  - delegated_digest.deletion_read(root) -> the reader shape every source has ({"items": [(identity, t, record)],
    "state", ...}): one record per FLAGGED deletion (a deleted JUDGE or OWNER entry, a deleted open finding), none for
    an unflagged one; each record holds source "deletion", t, mod, shard_class (JUDGE|OWNER|HOLDER|...), kind, was_open;
  - contracts.blind.project_digest(date, None, cut, [record], status) (the call delegated_digest makes) yields the class "ledger deletion" with the mod, and the page
    data carries none of the entry's text, subject or commit subject (no record text reaches the page).
No alarm and no refusal anywhere: the monitor never gates.
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
SRC = os.path.dirname(RIMFLOW)
sys.path[:0] = [RIMFLOW, SRC]
import modledger as M                                            # noqa: E402

res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:400]))


def attempt(fn):
    try:
        return fn(), None
    except Exception as e:                       # noqa: BLE001 — an unbuilt contract is a FAIL
        return None, "%s: %s" % (type(e).__name__, e)


try:
    import delegated_digest as DD                                # noqa: E402
    from contracts import blind as BL                            # noqa: E402
except Exception as e:                           # noqa: BLE001
    DD = BL = None
    print("import failed: %s" % e)
check("deletion is a digest source in both the contract and the digest",
      BL is not None and "deletion" in BL.SOURCES and "deletion" in DD.SOURCES and "deletion" in DD.LATER_SOURCES)
root = tempfile.mkdtemp(prefix="ml_deldigest_")
MOD = "FlowWorks"
g = lambda *a: subprocess.run(["git", "-C", root, *a], capture_output=True, check=True, timeout=60)  # noqa: E731
g("init", "-q", "-b", "main"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
os.makedirs(os.path.join(root, "design", "concepts", MOD))
M.append(root, MOD, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
# fixture inputs in the entry standard's shape (adopted by RIMMANDRAKE_ADOPT_ENTRY_STANDARD_IN_MODLEDGER_FOURTEEN_OWED);
# the subject still carries SECRET, so the page check below is unchanged in strength
fid, _ = M.append(root, MOD, "JUDGE.J1", "finding.open", "finding:RIMMANDRAKE_KEEP_SECRET_SUBJECT_OFF_DIGEST_PAGE",
                  run="J1", evidence=["run:J1"],
                  body={"class": "problem", "bars": [], "tags": ["code"], "text": "SECRET FINDING TEXT",
                        "proposed_fix": "the precise fix, also secret", "accept": "none, fixture"})
did, _ = M.append(root, MOD, "STEWARD", "decision", "q:own", body={"text": "own decision"}, authority={"why": "t"})
g("add", "-A"); g("commit", "-q", "-m", "base")
M.delete(root, MOD, [fid, did])
g("add", "-A"); g("commit", "-q", "-m", "SECRET COMMIT SUBJECT")
r, err = attempt(lambda: DD.deletion_read(root))
items = (r or {}).get("items") or []
recs = [it[2] for it in items if isinstance(it, (list, tuple)) and len(it) == 3]
check("deletion_read returns one record, for the flagged judge finding only", len(recs) == 1, err or items)
rec = recs[0] if recs else {}
check("the record names the mod, the shard class, the kind and that it was open",
      rec.get("source") == "deletion" and rec.get("mod") == MOD and rec.get("shard_class") == "JUDGE" and
      rec.get("kind") == "finding.open" and rec.get("was_open") is True, rec)
now = datetime.datetime.now(datetime.timezone.utc)
status = {s: {"state": "measured", "fault": "none", "malformed": 0, "all_time": 1} for s in (BL.SOURCES if BL else [])}
page, err = attempt(lambda: BL.project_digest(now.date().isoformat(), None, now + datetime.timedelta(days=1), recs,
                                              status))
blob = json.dumps(page, default=str) if page is not None else ""
check("the digest projects it as a ledger deletion", "ledger deletion" in blob, err or blob[:300])
check("the projection names the mod", MOD in blob, err or blob[:300])
check("no entry text, subject or commit subject reaches the page", page is not None and not any(
    s in blob for s in ("SECRET", "F_SECRET_SUBJECT", "precise fix")), err or blob[:300])
shutil.rmtree(root, ignore_errors=True)
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)
