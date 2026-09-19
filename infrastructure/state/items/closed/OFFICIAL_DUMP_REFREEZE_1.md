# OFFICIAL_DUMP_REFREEZE_1 — re-froze at 584 mods

Owner-authorized 2026-08-29 (verbatim: "we need to re-freeze the official mod list again,
and likely regenerate your official dump files"). Spec was precise; executed exactly as
written.

## What happened
1. Fresh full-list cold load completed; `dump_request.txt` (armed `all`) produced
   `DefDump/captures/2026-08-29T13-30-02Z/`.
2. Verified the new capture's `manifest.json` before freezing anything: `modCount: 584`,
   both `meathax.showmeyourtools` and `mlie.showmeyourhands` present (the two mods added
   since the prior official freeze).
3. `refresh.py --freeze` (dry run) confirmed it resolved the new capture and would
   supersede `OFFICIAL-2026-08-21T22-44-59Z` — read before writing.
4. `refresh.py --freeze --by owner` — wrote `OFFICIAL-2026-08-29` to
   `infrastructure/state/dumps/REGISTRY.jsonl`, sealed, `modlist_sha 1742630eb6253187`.

## Watch out
⚠️ **`defs.sqlite` is derived and explicitly OUTSIDE the freeze** (`refresh.py`'s own
note field says so) — it still pointed at the OLD 582-mod capture's provenance
immediately after freezing (freezing the capture does not rebuild the derived db).
`refresh.py --all` was run separately, in the background, to bring it current; that is
routine derived-artifact maintenance, not part of what "frozen" means here.

## criteria
- [x] New capture verified 584 mods including both newly-added packageIds, before freezing.
- [x] Frozen via the owner-only `--freeze --by owner` path, dry-run read first.
- [x] Supersession recorded: `OFFICIAL-2026-08-29` supersedes `OFFICIAL-2026-08-21T22-44-59Z`
      in `REGISTRY.jsonl`.
