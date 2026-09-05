## spec
Filed during standing dirty-code-review loop wave 38 (2026-09-05). A fresh
review of `src/RimStarWars/Armoury/Patches/Armoury_MeleePower.xml` found it
no longer matches the output its own generator
(`src/RimStarWars/Armoury/Source/gen_armoury_patch.py`) would produce today
from the SAME anchor values recorded in the file's own comments:

- `OuterRim_VibroAxe` edge: file has `21→27`; current `BANDS["vibro"]` /
  `SOURCE_RANGE["vibro"]` constants compute `21→38`.
- `guy762_vaxe` edge: file has `30→35`; current constants compute `30→42`.
- Shared-declarer lightsaber write: file has `hilt:12→15, point/edge:28→35`;
  the mod's own README (`src/RimStarWars/Armoury/README.md`) documents the
  intended/shipped value as "all 15 lightsabers now identical at 99" — the
  file's actual 28→35 is nowhere near that.

**This is not dormant.** `mandrake.rsw.armoury` IS active in the live
595-mod `ModsConfig.xml` (verified 2026-09-05, contradicting the mod's own
README which claimed it was not enabled — that README section has been
corrected). Ledger items `ARMOURY_LIGHTSABER_FINDMOD_1` and
`ARMOURY_SOUND_PATHS_RSW_PREFIX_1` show BENCH/FOUNDRY actively deploying and
live-verifying other parts of this same mod against the full campaign list
across 2026-09-04/05. So the stale melee values in this file are shipping
in the actual current game right now, not a pre-release artifact.

## why not fixed on the spot
The reviewing subagent declined to regenerate: the live/local def dump
available at review time only reflects the current minimal (~17-mod) test
load, not this mod's ~589/595-mod target stack. Re-running
`gen_armoury_patch.py` against a dump scoped to the wrong mod set would
silently produce a differently-wrong file (see `patch-a-curated-artifact-
never-reallocate` — a partial-input regenerate churns output disproportionately).

## 🔴 DO NOT just re-run the generator — it has its own regression (found 2026-09-05)
I tried running `python3 src/RimStarWars/Armoury/Source/gen_armoury_patch.py`
in place against the current full-595-mod dump (fingerprint `3174253fcd55f69c`,
`DefDump/defs.sqlite`, 78831 defs) to see what it would produce. It DID
overwrite `Armoury_MeleePower.xml` and `Armoury_RangedDamage.xml` in place
(no dry-run/diff-to-temp flag exists on this script — reverted with
`git checkout --` before committing, so the repo is undamaged).

The regenerated `Armoury_MeleePower.xml` **re-added the 21 dead lightsaber-
variant `PatchOperationReplace` entries** (Force_Broadsaber, Force_Darksaber,
Force_Lightsaber_Crossguard/Curved/Custom/Dual/Inquisitor/Shoto) that
`LIGHTSABER_MELEE_PATCH_FAIL_1` (2026-09-01) deliberately removed, because
the donor mod no longer gives those ThingDefs their own `<tools>` list (they
inherit from `Force_LightsaberBase` now) — those xpaths match 0 nodes and
made the whole wrapping `PatchOperationFindMod` report `failed` on every
load. The shipped file's own comment says this outright: "a future
regenerate should not re-add the per-variant entries unless the donor mod
restores per-variant tools" — and the generator does exactly that anyway.

So the generator's declarer-resolution does not know about this donor-mod
change and will reintroduce the same load-time failure every time it's run.
**Before this item can close, `gen_armoury_patch.py` needs a fix (skip a
ThingDef's own `tools/li` xpath when that ThingDef doesn't declare its own
`tools`, or an explicit skip-list keyed to the same donor-mod fact
LIGHTSABER_MELEE_PATCH_FAIL_1 recorded) — then re-run, diff to a temp path,
review the diff by hand against both known-good fixes before overwriting
the shipped file.**

## progress 2026-09-05
The lightsaber declarer-resolution bug described above IS fixed
(`gen_armoury_patch.py`, commit `b5da9f9b`) — `self_supplied_tools_defnames()`
now correctly skips the 8 lightsaber variants. Verified: 35/35 selftests
pass, `Armoury_RangedDamage.xml` unaffected, shipped `Armoury_MeleePower.xml`
values unchanged (only its stale explanatory comment was wrong; corrected).

**BLOCKED on a second, separate gap** before the vibro values can be
regenerated: filed as `ARMOURY_SWMODS_DONOR_GAP_1` — `SW_MODS` doesn't
recognize the absorbed KotORWeapons/JDS-Armory donor names, so a full regen
right now silently drops their vibro-blade tuning blocks entirely. Fix that
first, or the "expected" vibro values this item originally cited
(OuterRim_VibroAxe 21→38, guy762_vaxe 30→42) may themselves be wrong.

## criteria
- A def dump fingerprint-verified current against the live full mod list
  (`ModsConfig.xml`, currently 595 active) is available.
- `gen_armoury_patch.py` re-run against that dump; new
  `Armoury_MeleePower.xml` diffed against the current shipped file to
  confirm the melee values move in the direction described above (or a
  deliberate reason is recorded for why they should not).
- `validate_patch.py` clean against the full list.
- Deployed and live-verified (a load with this file changed, read back via
  bridge or dump) before closing.
- A fresh, separate code review of the regenerated file finds nothing, and
  it is marked clean via `code_review_status.py mark-clean` (fixing this
  bug does not itself clean the file).
