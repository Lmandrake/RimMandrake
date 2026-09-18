# DIRTY_CODE_REVIEW_LOOP_RESTART_13

Continuity note for the standing dirty-code-review loop (FOUNDRY). Successor to
`DIRTY_CODE_REVIEW_LOOP_RESTART_12` — read that file (and its own chain) for
fuller history. This file is the short version: what this session did,
current numbers, and what to do first.

## Where things stand

`infrastructure/state/CODE_REVIEW_STATUS.json`, freshly re-listed this
session: **2897 clean / 2942 tracked (98.5%)**, up from RESTART_12's
2896/2942. Re-run `list` fresh rather than trusting this number — it decays
fast on a shared four-seat worktree.

**45 files are DIRTY right now.** Notable clusters, still open:

- `src/RimMandrake/FlowWorks/*` (9 files, LiquidTypes + About.xml + Mod.cs) —
  `LIQUID_BOTTLE_LOOP_1` is STILL `doing` (re-verified this session via
  `rimflow show`); leave this cluster alone until it closes.
- `src/RimStarWars/SWBestiary/*` (7 files) — `MLIE_FAUNA_ABSORPTION_1` is
  STILL `doing`, actively porting species (Pass 12 committed same day this
  session ran: Gizka/Grank/GreaterKraytDragon/Hawkbat). Confirmed via both
  `rimflow show` and recent commit history — do not touch, not even
  file-by-file, while this stays `doing`.
- `src/RimMandrake/Utils/artpipe/*` (5 files, one more than RESTART_12 saw —
  `common.py` joined the dirty set mid-session, a concurrent agent's edit).
- `src/RimMandrake/Utils/code_review_status.py` — the tool that owns this
  very registry; dirty since 2026-09-09, still unreviewed. Careful,
  standalone pass owed.
- `src/RimMandrake/rimflow/model.py` — still deliberately deferred
  ("pending an owner ask"); do not pull it cold.
- **New this session, by design**: `src/RimMandrake/Greentide/About/About.xml`,
  `RM_MapComponent_CrossBiomeChurnmud.cs`, `RM_GreentideMod.cs`,
  `RM_RootCausewayBiomeExtension.cs` (EnvironmentalHazards),
  `RUT_Greentide.xml`, `RUT_TarMoat.xml` (UtinniPatches) — all previously
  CLEAN, all now DIRTY because this session's `RM_Churnmud` rename touched
  them (see below). Per the standing rule, a fix does not clean a file, so
  these are left dirty on purpose pending a future full-file review — I only
  patched specific lines/comments in most of them, not a complete read (the
  two I did read whole — `RM_MapComponent_CrossBiomeChurnmud.cs` and the
  Greentide Terrain/Biome defs already marked clean — are covered below).
  `RUT_Greentide.xml` and `RUT_TarMoat.xml` in particular got only a
  targeted read around the touched lines, not a full-file review — good
  next-session candidates precisely because they're already halfway looked
  at.

## What this session actually did

1. Re-ran `code_review_status.py list` fresh (46 dirty at start). Confirmed
   `LIQUID_BOTTLE_LOOP_1` and `MLIE_FAUNA_ABSORPTION_1` both still `doing`
   via `rimflow show` — skipped FlowWorks/LiquidTypes and all of SWBestiary
   entirely, per the brief.
2. Confirmed all three of RESTART_12's next-picks are live, active mods
   (`mandrake.rsw.starwarsraces`, `mandrake.rm.aftermath`,
   `mandrake.rm.greentide` all present in the live
   `ModsConfig.xml` — reachable from this WSL seat at `/mnt/c/...`, unlike
   the Mac).
3. **`src/RimMandrake/Aftermath/Source/*`** (3 files: `AftermathRuleRunner.cs`,
   `QueuedAftermathMarker.cs`, `RM_Aftermath.csproj`). Read whole; csproj's
   `<Compile Include>` list matches `Source/` exactly. No functional bugs.
   Marked clean at `8a0a88e18`.
4. **`src/RimMandrake/Greentide/*`** (3 files: `RM_Greentide_Biome.xml`,
   `RM_Greentide_Hediffs.xml`, `RM_Greentide.csproj`) — and in the course of
   reviewing the biome def, found a **real, live bug**:

   **`RM_Churnmud` defName collision.** `mandrake.rm.greentide` and
   `mandrake.rm.flowworks` each shipped an active `TerrainDef` named
   `RM_Churnmud` with unrelated content — Greentide's mire+swallow hazard
   (`RM_MireExtension`, pathCost 34) vs FlowWorks's plain MarshBase-derived
   viscosity mud grade (pathCost 60, no hazard). Both mods are live in the
   current `ModsConfig.xml`. Whichever mod's def loader ran last would
   silently win the whole defName, including inside
   `RM_MapComponent_CrossBiomeChurnmud`'s `DefDatabase<TerrainDef>
   .GetNamedSilentFail("RM_Churnmud")` lookup — meaning Greentide's own
   flagship cross-biome opt-in feature could have been painting the WRONG
   terrain (FlowWorks's inert mud) onto other biomes' maps while logging a
   message that claimed the mire hazard was applied.

   Fixed by renaming Greentide's def to `RM_GreentideChurnmud` everywhere it
   is produced or consumed, and leaving FlowWorks entirely untouched (still
   `doing`, off-limits): `RM_Churnmud_Terrains.xml`, `RM_Greentide_Biome.xml`,
   `RM_MapComponent_CrossBiomeChurnmud.cs`, `RM_GreentideMod.cs`,
   `Greentide/About/About.xml`, plus two cross-mod consumers,
   `RUT_Greentide.xml` (a real cross-reference inside `basinTerrains`) and
   `RUT_TarMoat.xml` (a comparison comment), and one illustrative doc-comment
   in `RM_RootCausewayBiomeExtension.cs` (EnvironmentalHazards, unrelated
   mod, kept accurate). Commit `7e8587cea`, pushed. `RM_Greentide_Biome.xml`,
   `RM_Greentide_Hediffs.xml`, `RM_Greentide.csproj` marked clean at
   `8a0a88e18` (full reviews, no other bugs). The other touched files
   (listed above) are left DIRTY on purpose — see above.

5. **`src/RimStarWars/StarWarsRaces/Defs/*`** (3 files: `SW_Genes.xml`,
   `RimMandrakePawnKinds.xml`, `RimMandrakeXenotypes.xml` — 157 GeneDefs/69
   PawnKindDefs/69 XenotypeDefs). First pass flagged ~40 "missing" gene
   cross-references per xenotype as an apparent catastrophic finding —
   **second look killed it** (dramatic-findings-need-a-second-look): those
   are genes from the mod's own DECLARED external dependencies (`Outland_*`
   from Neronix17.Outland.Genetics, `Turn_Gene_*` from Turnovus's Integrated
   Genes, `BS_*`/`Aptitude*`/`Body_*` from Big and Small) plus vanilla
   Biotech (`Skin_*`, `Hair_*`, `Robust`, `Fertile`, etc.) — About.xml is
   explicit that these "remain theirs" and are dependencies, not copies. Also
   checked: many xenotypes list several same-category genes together (e.g.
   8 skin-color genes on one species) — this is a known Biotech
   exclusionTag trick (generation picks one per exclusion group) inherited
   from the curated donor (`[BTD] Xenotype REMIX`), not a bug; couldn't
   verify the exact runtime pick behaviour since RimSage is unavailable on
   this WSL seat, so treated as UNMEASURABLE rather than asserted either way.
   Confirmed: no duplicate defNames anywhere in the three files; every
   xenotype/pawnkind cross-reference resolves; the 4 Jawa-specific genes
   About.xml says are "authored here" live in sibling files
   (`Jawa_Head.xml`/`Jawa_Skittish.xml`/`Jawa_EyeColours.xml`) within the same
   Defs/GeneDefs folder, not SW_Genes.xml itself — correct, not a gap. No
   functional bugs found. Marked clean at `8a0a88e18`.

Total this session: **9 files reviewed and marked clean** (3 Aftermath + 3
Greentide + 3 StarWarsRaces), **1 real live bug found and fixed** (the
RM_Churnmud collision, 8 files touched across 3 mods), **0 other functional
bugs**. `run_selftests.py`: 56/58 (2 pre-existing, unrelated failures —
`selftest_one_path_seam.py`'s LocalLow-literal check flags
`artpipe/build_flora_legibility_sheet.py`, and `selftest_art_checks.py`'s
calibration checks fail against Anooba/Nuna/Gizka sprites mid-port under
`MLIE_FAUNA_ABSORPTION_1` — neither touches anything this session reviewed).
Commits `7e8587cea` (the fix), `8a0a88e18` (mark-clean + status file), both
pushed.

One git-lock incident: a `.git/index.lock` appeared mid-session with no
owning process found via `lsof`/`fuser`/`ps` (checked, waited 8s, re-checked
— still no holder). Removed per the repo's "err toward allowing" convention.

## Recommended next steps, in order

1. `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_Greentide.xml` and
   `.../Defs/TerrainDefs/RUT_TarMoat.xml` — already half-read this session
   (the RM_Churnmud rename touched both), good next candidates for a full
   pass to actually mark them clean.
2. `src/RimMandrake/Utils/code_review_status.py` — the tool itself, dirty
   since 2026-09-09, still owed a careful standalone pass (RESTART_12 also
   flagged this and it didn't get done).
3. `src/RimMandrake/Utils/artpipe/*` (5 files now, `common.py` newly dirty).
4. Re-verify `LIQUID_BOTTLE_LOOP_1` and `MLIE_FAUNA_ABSORPTION_1` before
   touching FlowWorks or SWBestiary — both were still `doing` this session;
   if either has closed, its cluster is fair game.
5. Always re-run `code_review_status.py list` fresh at the start of the next
   session rather than trusting this file's 2897/2942 numbers.
