# QUEUE_GITHUB_MIRROR_1 — GitHub issues as a queue visualizer, pilot

## spec
One-way mirror: rimflow OPEN items become GitHub issues on Lmandrake/RimMaster
(issue title = item ID, full ask in the body, seat/needs as labels); items that
go terminal after mirroring get their issue closed. ⭐ events.jsonl STAYS the
truth — GitHub is a visualizer; deleting every issue loses nothing. No backfill
of the ~2,600 historical events.

## state 2026-08-28 — built offline, blocked ONLY on owner auth
- `src/RimMandrake/rimflow/github_mirror.py` — dry-run by default, `--apply`
  executes, `--ensure-labels` creates the label set. Replays the ledger via
  `rimflow.model.replay()`; mirror map committed at
  `infrastructure/state/ledger/github_mirror_map.json` (provenance, not cache).
- Dry run verified: 30 open items -> 30 creates, 0 errors.
- `gh` 2.76.2 installed user-local at `~/.local/bin/gh` (on PATH via .zshrc).
- ⚠️ MEASURED: the repo is PUBLIC — unauthenticated GET on
  api.github.com/repos/Lmandrake/RimMaster returns 200. Mirrored issues will be
  publicly visible. The repo's full content (canon, design docs) is already
  public, so the marginal exposure is small — but the filing title assumed
  private, so this needs the owner's nod.

## verify
`gh auth login` (owner — interactive), then:
`python3 src/RimMandrake/rimflow/github_mirror.py --ensure-labels --apply`
and eyeball https://github.com/Lmandrake/RimMaster/issues .

## criteria
- 30 open items visible as issues with seat/needs labels; closing an item via
  `rimflow close` + a re-run closes its issue.
- The pilot is judged by the owner actually looking at the issues page; if it
  earns nothing in a week, drop it and delete the issues — the ledger never knew.

## Watch out
- The mirror NEVER writes the ledger; keep it that way — a two-way sync is the
  drift machine the charter forbids.
- Re-running `--apply` is idempotent via the fingerprint in the map; deleting
  the map re-creates all issues (duplicates) — the map is committed for a reason.
