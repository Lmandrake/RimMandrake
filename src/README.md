# src/ — source we author

**Tier rule: if we wrote it and a machine consumes it, it is here.** Mods, tools,
scripts, assemblies, benches. Python is the working version; where compilable
source exists it is kept in lockstep with it.

## The split

A new mod goes in `src/RimMandrake/`, `src/RimStarWars/` or `src/RimUtinni/`. The test for each folder:
`infrastructure/STRUCTURE.md` §The `Jawa/` vs `RimMandrake/` split. No new mod goes in `src/Jawa/`.

The owner's test for art-fix mods: *could someone who owns only the donor mod subscribe to this and have it
work?*

## 🔴 Writing a file here is not deploying it

The game reads
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\<ModName>` and
**nothing syncs it from this tree.** Run `deploy_custom_mods.py` (plan-only),
read the plan, then `--apply --mod <Name>`. A bare `--apply` pushes every mod in
the tree including another seat's half-finished work.

## Run-artifacts stay beside their generator

A script's outputs — `mapsynth/runs/`, `art_bench/_review/` — are **gitignored and
live next to the code that made them**, not in `observed/`. `observed/` is tied to
contact with a live game; a PNG our own script rendered is not an observation of
anything.

## Naming, for NEW work only

The packageId, the prefix and the namespace of a new mod follow its tier: `design/NAMING_SCHEME_PLAN.md`.

The planned `MODLIST.md` here is **hand-authored** — what this tier's code assumes exists.

⏳ **`MODLIST.md` DOES NOT EXIST YET.** This section describes what it will be,
not what is here — verified 2026-08-13, `find` returns nothing. **Do not cite it
as though it exists**; that is the same silent-failure shape as a `loadAfter`
naming a mod that was never installed. Build it or delete this paragraph.
