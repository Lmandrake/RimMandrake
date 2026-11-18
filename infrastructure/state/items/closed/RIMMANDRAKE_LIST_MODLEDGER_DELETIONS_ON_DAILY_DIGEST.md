# RIMMANDRAKE_LIST_MODLEDGER_DELETIONS_ON_DAILY_DIGEST

His ruling 2026-11-15 ~10:16 PM PST, via the Conductor: "Delete on sight. I really don't think that's going to be abused
to pass a judge. But we can monitor." Built by RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE's run: any
writer deletes a mod-ledger entry (`modledger.py delete`), the lint accepts whole-line deletions and refuses in-place
edits, and `modledger.py deletions` is the monitor (counts per mod and writer from git; `flagged` = every deleted JUDGE
or OWNER entry and every deleted open finding). Owed here: putting `flagged` on the Conductor's daily digest
(`src/RimMandrake/rimflow/delegated_digest.py`) through its blind contract (`src/RimMandrake/contracts/blind.py`): a
new source, so it touches closed types, the field allow-list and the leak-proof page, and was not changed in the
filing run. Monitor, not gate: no alarm, no refusal.

Known limit: git carries no seat (every commit has his git identity), so the monitor cannot tell a holder's deletion of
a judge finding from the judge's own; it flags every deleted JUDGE or OWNER entry, and names the commit.

## spec

- `delegated_digest.deletion_read(root)` over `modledger.deletions(root, since)`; "deletion" in contracts.blind
  `Source`, `RAW_FIELDS`, `_record` (class "ledger deletion", mod from the domain, shard class, kind, was_open);
  `SOURCES` and `LATER_SOURCES` in delegated_digest; their selftests (`selftest_blind_contract.py`,
  `selftest_delegated_digest*.py`) extended.

## verify

Acceptance test: `python3 src/RimMandrake/rimflow/acceptance/modledger_deletion_digest_accept.py` — expected `PASS 6/6`.
Watched failing at filing: `FAIL 5 of 6` (no deletion source; the no-leak clause passes only because the page is empty).
Sanity probe at filing: the same project_digest call over a `release` record shows its class and mod.

## criteria

- the acceptance test passes; the digest and blind-contract selftests stay green.
