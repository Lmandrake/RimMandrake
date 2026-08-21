## spec
🔴 **`NEXT_RELOAD.md` §1.0 step 0 and §1a are wrong on their central fact, and
they state it as urgent.** Both say the live def dump is from **2026-08-14
01:20**, "before eleven mods left", and conclude that every
`validate_patch.py --defs` run is checking against a def universe that no
longer exists. Raised by CHECK (`e0997c0`), verified independently by REP:

- That date was read off the `defs/` **FOLDER** mtime. The dump overwrites its
  files in place and never adds or removes one, so the folder date does not
  move while the contents do.
- **The manifest is the authority.** `manifest.json`: `capturedUtc
  2026-08-15T15:10:11Z`, `mode all`, `gameVersion 1.6.4871 rev591`, 576 mods,
  529 def files. Every file under `defs/` is stamped **Aug 15 08:10** local
  (= 15:10Z). Taken during this morning's C37 load, WITH the races mod and
  with all three donors absent — the current configuration.

⚠️ **REP over-corrected here and BUILD caught it. The dump is fresh in TIME
but not in SET, and only one direction of the staleness is safe.** Verified by
REP against both files: manifest `modCount` **576**, live `activeMods` **575**,
and the diff is exactly one — `regrowth.botr.boilingforest` in the dump, and
NOTHING live is missing from the dump.

⇒ Every def that loads in game IS represented, so `--defs` cannot miss a real
def. **The risk is one-way and it is live:** the dump still holds defs from a
mod that no longer loads, so an xpath onto those defs validates CLEAN and
matches nothing in game. It already bites one of ours —
`src/Jawa/Jawa_Patches/Patches/JawaWorld_BiomeMix.xml:140` sets a `scoreOffset`
on `RG_BoilingForest`, which is still in the dump's `BiomeDef.json` and
`IncidentDef.json`. That patch reports clean today and is a no-op in game.
`refresh.py`'s STALE verdict was therefore CORRECT — it keys on the load-set
fingerprint, not on age, and it named this exact mod.

The wording for the board: *the dump is current as of 2026-08-15T15:10:11Z but
was captured at 576 mods against a live 575; `--defs` is sound except for
anything touching `regrowth.botr.boilingforest` defs.* The re-dump is armed, so
the next load closes it. REP's own
`promote-the-defdump-arming-out-of-optional-6ea3c7` was filed on the bad
premise; correct both sections against this.

Two non-problems, so nobody chases them: the mod folder is still on disk at
`...\294100\3565675704` — unlisted, not unsubscribed, installed-but-inactive;
and `src/Jawa/Jawa_Doctrine/About/About.xml` names it in **loadAfter**, not
`modDependencies`, which exerts no constraint on an inactive mod and logs
nothing. Harmless, leave it.

What survives the correction: arming the dump is still right, because it
re-reads after this window's deploys and costs 18.7s. CHECK already armed it
(13:27). What must go is the urgency and the "stale universe" reasoning — if
any item was deferred on that premise, it is not blocked.

**Read freshness from `manifest.json` `capturedUtc`, never from a folder
mtime.** That is the reusable half.

## verify
§1.0 step 0 and §1a state the manifest date and the manifest as the source;
neither claims the dump predates the mod-set change.

## criteria
EMPTY — offline.

## notes
**Imported from `queue/DECIDE_ARCHIVE.md`. Its `state:` read, verbatim:**

⛔ v2 — **OWNER RULING 2026-08-15, blanket triage.** Produces no content and does not
reach the frozen world. Parked, not lost.
