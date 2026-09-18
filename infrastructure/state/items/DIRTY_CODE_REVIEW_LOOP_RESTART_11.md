# DIRTY_CODE_REVIEW_LOOP_RESTART_11

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor to
`DIRTY_CODE_REVIEW_LOOP_RESTART_10` — read that file (and its own chain) for the
fuller history. This file is the short version: what this session did, current
numbers, and what to do first.

## Where things stand

`infrastructure/state/CODE_REVIEW_STATUS.json`, freshly re-listed this session
(the `list` command that hung for RESTART_10 ran clean in ~seconds this time —
treat the "hangs on the shared mount" note as transient, not standing):
**2882 clean / 2942 tracked (98.0%)**, up from the 618/635 figure RESTART_10
carried — the scope has grown a great deal since 2026-09-04 (Rot, FlowWorks
Pits/LiquidTypes, EnvironmentalHazards, more StructureInjections/Inhabited
content), so that older percentage is not comparable to this one; always
re-run `list` fresh rather than diffing against an old count.

**60 files are DIRTY right now** (`grep '^DIRTY' <freshly captured list>`).
Nearly all of them are "content changed since clean mark" on files a *different*
concurrent build touched after its own clean mark — i.e. real, current backlog,
not stale bookkeeping. Notable clusters, all still open for the next session:

- `src/RimMandrake/FlowWorks/Source/LiquidTypes/*` + matching Defs (7 files,
  dirtied 2026-09-17 by `LIQUID_BOTTLE_LOOP_1`'s tank build) — re-verify that
  item's state before reviewing; it may still be `doing`.
- `src/RimMandrake/Pyrelands/*` (7 files, mixed 2026-09-09..11 marks)
- `src/RimMandrake/EnvironmentalHazards/Source/RM_HediffComp_EnvironmentalExposure.cs`,
  `RM_EnvironmentalHazards.csproj`, `RM_EnvironmentalHazardsMod.cs` were dirty
  from the `ROT_*` wave (b8d87d692 and siblings) but were NOT reviewed this
  session — see below, a *different* 5 EnvironmentalHazards files were done.
- `src/RimStarWars/SWBestiary/*` (Mlie wave C, 6 files, 2026-09-12) — brief
  said this directory is actively being extended by a sibling agent; left
  untouched this session per that instruction.
- `src/RimMandrake/Utils/modcheck/*` (7 files, 2026-09-12) — CLAUDE.md itself
  documents specific known defects in this package (status.py reads a stored
  field instead of re-deriving; `NORTH_STAR_PIT_PILOT_1` gates on it). A full
  review here should cross-check against those already-known findings rather
  than re-discover them fresh.
- `src/RimMandrake/Utils/artpipe/*` (4 files, 2026-09-12)
- `src/RimStarWars/StarWarsRaces/Defs/*` (Genes/PawnKindDefs/XenotypeDefs,
  2026-09-05)
- `src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` and
  `design/Jawa/fauna/BiomeCast_Ashkarr.xml` (both dirty, `[x8]`/`[x6]` marks —
  heavily-iterated design file, check current state before assuming stale)
- `src/RimMandrake/rimflow/model.py` — deliberately deferred per RESTART_9/10
  ("pending an owner ask"); that deferral still holds, don't pull it cold.

## What this session actually did

Ran `code_review_status.py list` fresh (worked fine, ~seconds — no hang this
time) and picked two small, clearly-reachable, non-racing batches:

1. **`src/RimMandrake/EnvironmentalHazards/`** — 5 files dirtied by the recent
   `ROT_*`/mod-activation wave (`Languages/English/Keyed/RM_EnvironmentalHazards_Keys.xml`,
   `Source/HazardTargeting.cs`, `Source/RM_EnvironmentalHazards.csproj`,
   `Source/RM_EnvironmentalHazardsMod.cs`, `Source/RM_HediffComp_EnvironmentalExposure.cs`).
   Confirmed the mod is live (activated in both mod lists at `9bf9ccf4e`).
   Full-file review: verified every one of the ~34 Mod Settings toggles is
   actually read by its named mechanism (grepped each field name outside the
   Mod class itself), and diffed the `.csproj`'s `<Compile Include>` list
   against the real `*.cs` files on disk — exact match, no orphaned or missing
   compile entries. No bugs found. Marked clean at `6d0c2bc2a`.
2. **`src/RimMandrake/WreckedMachines/About/About.xml` +
   `Defs/ThingDefs_Buildings/Buildings_WreckedMachines_AutomatedSmelter.xml`**
   — 2 files, dirty since 2026-09-05. Confirmed this is a VALIDATED north-star
   mod (unrelated to its own `## north star` section, which this touch does
   not go near). Verified all three tiers' `texPath`s resolve to real PNGs on
   disk, the `WreckedMachines_HideDonorSmelter.xml` patch and
   `RM_WM_AutomatedSmelterRestoration` research def it references both exist.
   **Found one real (minor) bug while reading the adjacent, out-of-scope,
   untracked `WreckedMachines_HideDonorSmelter.xml`**: its own verification
   comment claimed our three tiers "carry their own designationCategory
   (WreckedMachines) or none" — false; all three actually carry
   `VFEFactory_Factories`, the SAME category as the donor def the patch hides.
   Not a functional bug (the category stays populated because our tiers keep
   it, so nothing disappears from the Architect menu) but inaccurate material
   per the standing "delete, don't leave wrong text standing" rule — fixed the
   comment in place. Marked the two in-scope files clean at `6d0c2bc2a`.

Total this session: **7 files reviewed and marked clean, 1 real (doc-accuracy)
bug fixed**, zero functional bugs found. Commit `6d0c2bc2a`, pushed.

## Recommended next steps, in order

1. Pull the next reachable, non-racing batch from the DIRTY list above —
   `modcheck/` (cross-checking CLAUDE.md's already-known findings first) or
   `Pyrelands/` are good next candidates; both are small and self-contained.
2. Re-verify `LIQUID_BOTTLE_LOOP_1`'s state before touching FlowWorks
   LiquidTypes — if it's still `doing`, leave it for whoever closes that item.
3. `src/RimStarWars/SWBestiary/` — only after confirming the sibling
   fauna-absorption pass (`MLIE_FAUNA_ABSORPTION_1`) isn't mid-commit; check
   file-by-file with `code_review_status.py check`, never a directory sweep,
   per the brief that flagged this risk.
4. Always re-run `code_review_status.py list` fresh at the start of the next
   session rather than trusting this file's 2882/2942 — it decays fast on a
   shared four-seat worktree.
