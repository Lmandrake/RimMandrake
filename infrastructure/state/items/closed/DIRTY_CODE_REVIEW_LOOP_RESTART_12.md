# DIRTY_CODE_REVIEW_LOOP_RESTART_12

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor to
`DIRTY_CODE_REVIEW_LOOP_RESTART_11` — read that file (and its own chain) for
fuller history. This file is the short version: what this session did, current
numbers, and what to do first.

## Where things stand

`infrastructure/state/CODE_REVIEW_STATUS.json`, freshly re-listed this session:
**2896 clean / 2942 tracked (98.4%)**, up from RESTART_11's 2882/2942 (98.0%).
Re-run `list` fresh rather than trusting this number — it decays fast on a
shared four-seat worktree (this session's own re-list picked up a brand-new
dirty file, `src/RimMandrake/Utils/gm_blackboard_shadow.py`, from a concurrent
agent's edit mid-session).

**46 files are DIRTY right now.** Notable clusters, still open:

- `src/RimMandrake/FlowWorks/Source/LiquidTypes/*` + matching Defs/About.xml
  (8 files) — `LIQUID_BOTTLE_LOOP_1` is STILL `doing` (re-verified this
  session via `rimflow show`); leave this cluster alone until it closes.
- `src/RimStarWars/SWBestiary/*` (7 files, Mlie wave C + Anooba/Boma races) —
  a sibling agent was reported actively porting new species here; check
  file-by-file with `code_review_status.py check`, never a directory sweep.
- `src/RimMandrake/Utils/artpipe/*` (4 files)
- `src/RimMandrake/Aftermath/Source/*` (3 files: AftermathRuleRunner.cs,
  QueuedAftermathMarker.cs, RM_Aftermath.csproj)
- `src/RimMandrake/Greentide/*` (3 files: biome def, hediff def, csproj)
- `src/RimStarWars/StarWarsRaces/Defs/*` (GeneDefs/PawnKindDefs/XenotypeDefs,
  dirty since 2026-09-05 — long-standing, small, good next batch)
- `src/RimUtinni/PawnFlavor/Patches/*` (2 files)
- `design/Jawa/fauna/BiomeCast_Ashkarr.xml` / `src/RimUtinni/UtinniPatches/
  Patches/BiomeCast_Ashkarr.xml` (heavily-iterated design files, `[x6]`/`[x8]`
  marks — check current state before assuming stale)
- `src/RimMandrake/rimflow/model.py` — still deliberately deferred per
  RESTART_9/10/11 ("pending an owner ask"); do not pull it cold.
- `src/RimMandrake/Utils/code_review_status.py` — the tool that owns this very
  registry; dirty since 2026-09-09. Reviewing the reviewer is legitimate work
  but deserves extra care (a bug here can corrupt the ledger for everyone).

## What this session actually did

Ran `code_review_status.py list` fresh (fast, no hang) and, per the brief,
took RESTART_11's own two recommended batches:

1. **`src/RimMandrake/Utils/modcheck/*`** (7 files: cli.py, floor.py,
   report.py, runner.py, selftest.py, status.py, suite.py). Cross-checked
   against CLAUDE.md's own documented findings:
   - `modcheck run <Mod>` rewriting the live `ModsConfig.xml` via
     `modlist_swap.py` — **confirmed still accurate**, left as documented
     (it's a designed, `finally`-guaranteed restore, not a bug).
   - **"`modcheck status` reads a stored field, prints `FluidCanals GREEN` /
     `FlowWorks NEVER RUN`" — found ALREADY FIXED** (`fa27e1cab`,
     `status.check_or_orphaned` + `doctor.py`, committed the same day, minutes
     *before* CLAUDE.md's claim was written). Live-verified: `modcheck status`
     now correctly prints `FlowWorks STALE [stored: GREEN]` and
     `Pits ORPHANED (no such mod folder) [stored: GREEN]` — the stored field
     only ever shows as a drift annotation, never as the live verdict. The
     dead `FluidCanals` key is retired too (`b110a7a2d`). **Corrected the
     stale CLAUDE.md claim in place** (kept the still-true "shows= appears in
     0 of N validation.py files" finding, count corrected 17 -> 54).
   - `selftest.py`: 18/18 pass. No functional bugs found in any of the 7
     files. Marked clean at `7fc491ebc`.
2. **`src/RimMandrake/Pyrelands/*`** (8 files: BiomeDef, Fulgurite/EmberGrass/
   Quickgrass/ScorchFruit ThingDefs, FireEcologyHook.cs + .csproj,
   RM_PyrelandsMod.cs). Confirmed live (`mandrake.rm.pyrelands` active).
   Verified every one of the 12 Mod Settings toggles is read at its call site
   (one, `plantGrowthStagesEnabled`, lands in the out-of-batch
   `PlantGrowthStages.cs` — checked anyway), the `.csproj`'s
   `<Compile Include>` list matches `Source/` exactly, and every
   cross-referenced def (genstep, terrain, filth) resolves. No functional
   bugs found — the biome def already carries a prior (2026-09-09) code-review
   correction to its own crossover-temperature arithmetic, still accurate.
   Marked clean at `e65687fbe`.

Total this session: **15 files reviewed and marked clean, 0 functional bugs
found, 1 stale CLAUDE.md doc claim corrected** (a real finding in its own
right: the underlying defect was fixed before the doc describing it was
written). Commits `7fc491ebc`, `e65687fbe`, both pushed.

One git-lock incident: a concurrent agent's crashed `git` process left a stale
`.git/index.lock` (owning PID confirmed gone via `ps`) that blocked the second
commit for ~30s. Removed once confirmed stale, per this repo's "the lock
errs toward allowing" convention for shared-tree tooling (same spirit as the
bridge-lock rule, though this is git's own lock, not `infrastructure/state/BRIDGE`).

## Recommended next steps, in order

1. `src/RimStarWars/StarWarsRaces/Defs/*` (3 files, dirty since 2026-09-05) —
   long-standing, small, self-contained, no known sibling-agent conflict.
2. `src/RimMandrake/Aftermath/Source/*` (3 files) or
   `src/RimMandrake/Greentide/*` (3 files) — both small, next candidates.
3. `src/RimStarWars/SWBestiary/*` — only after confirming no sibling agent is
   mid-edit there right now; check file-by-file with `code_review_status.py
   check`, never a directory sweep.
4. Re-verify `LIQUID_BOTTLE_LOOP_1`'s state before touching FlowWorks
   LiquidTypes — if still `doing`, leave it.
5. `src/RimMandrake/Utils/code_review_status.py` reviewing itself is fair
   game but should get a careful, standalone pass (it's the tool the whole
   loop trusts).
6. Always re-run `code_review_status.py list` fresh at the start of the next
   session rather than trusting this file's 2896/2942 numbers.
