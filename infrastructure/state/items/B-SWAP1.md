## spec
`src/RimMandrake/Utils/modlist_swap.py:60-64`. `snapshot()` stamps a new
`ModsConfig.PRESWAP.<ts>.xml` on **every** swap and never compares it to
anything:

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(STORE, "ModsConfig.PRESWAP.%s.xml" % stamp)
    shutil.copy2(LIVE, dst)

Measured 2026-08-20: **five** PRESWAP files had accumulated, and md5 proved
**all five were exact duplicates** of the tracked `FULL.LATEST` / `MINIMAL`
already sitting beside them. The cleanup pass deleted them; without a fix
they come back at the next swap, one per swap, forever.
🔑 **The fix is small and the tool already has the piece it needs** — `md5()`
is defined at line 27. Before writing, hash `LIVE` against every file already
in `STORE`; if it matches one, skip the copy and return that path instead.
A backup identical to a file we already keep is not a backup.
~~⚠️ Also a tracked duplicate: `ModsConfig.FULL.20260819_201527.xml` is
md5-identical to `FULL.LATEST`.~~ ⛔ **VOID 2026-08-20** — the owner changed the
worldmap/terrain texture mods that same day, `FULL.LATEST` became the 576 list,
and the timestamped file is now **the only copy of the 578 list**. It is not a
duplicate and must not be deleted. The pruning half of this item stands; this
half does not.
⚠️ PRESWAP files are gitignored (`.gitignore:206`), so this was only ever a
disk problem, never repo bloat.

## verify
run a swap twice with no mod-list change; `ls infrastructure/state/modlists/`
gains no new PRESWAP file on the second run.

## criteria
the backup store holds one copy of each DISTINCT list, and nothing else.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20. `modlist_swap.py` `snapshot()` now hashes the live file
against **every** `.xml` already in the store and returns the existing path
instead of writing a duplicate.
verify output, two consecutive calls with no mod-list change:
  `snapshot : skipped, identical to ModsConfig.FULL.LATEST.xml`
  `snapshot : skipped, identical to ModsConfig.FULL.LATEST.xml`
  `same: True`   — and `ls infrastructure/state/modlists/` is unchanged.
🔑 **The check is against the WHOLE store, not just FULL and MINIMAL**, which is
what makes the void half of this item safe: `ModsConfig.FULL.20260819_201527.xml`
is the only surviving copy of the 578 list, and a store-wide comparison keeps it
as a distinct kept file rather than treating it as a duplicate to prune.
It also now prints one line saying which path it took, so a swap says whether it
archived anything.
