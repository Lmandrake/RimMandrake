# FOUNDRY_HANDOFF_202610221110 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610220323`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward
Shift 2026-10-22 (owner AFK ~midnight; order: keep 1-2 helpers going, offline only, then Webworks/Rot): ~25 Sonnet/Opus review helpers cleared nearly every DIRTY C#, Python and ~475 of 582 XML in the code-review ledger and fixed ~60 real bugs, ALL pushed; the review loop item DIRTY_CODE_REVIEW_STANDING_LOOP_1 is NOT closed (standing loop). What remains is owner-decision material, collected below and in `design/RimMandrake/webworks_open_questions_2026-10-22.md`, `rot_open_questions_2026-10-22.md` and `design/RimMandrake/review_findings_2026-10-22/{dead_patches,ruled_values_questions,shell_bodypart_blast_radius}.md` (copied into `design/RimMandrake/review_findings_2026-10-22/`). Nothing was deployed or run live (BENCH held the bridge, game up). (filed: lessons)

## What the owner should see
- Cards waiting, in order: Webworks (8) and Rot (7) question files; Wave 4 gap (`design/RimMandrake/wave4_sheet_gap_2026-10-22.md`: tribals, wreckedmachines, Greentide, roaches, Webwork-in-paint); leaning-scrub purge conflicts (Igitz, MossBeetle, Mudhorn x2, Nysyllin) and Kybuck pick; Taozin D/F/I, Insectomorph, crate pictures.
- Review findings that touch his rulings: Tenant + StrandingPools vanish pawns/animals with no readable sign; per-biome SunHeatExtension in 4+ biome defs (DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES); BiomeGlowPatches glowMultiplier; Absorbed_Cephaloids `Shell` BodyPartDef (2500 HP indestructible) clobbers vanilla Shell for 28 bodies (rename to JOE_Shell needs OK); RSW_Shyrack frame 4 files are `_44_` (fix = drop to 3 frames: his call); durrok 6 / mullgoth 5 sizes lost (card in review_findings_2026-10-22/ruled_values_questions.md).
- Restored by me citing rulings: Gutkurr/Wraid MoveSpeed 4.4 (his 2026-09-09 card), Rust Cathedral + Forge mech-cluster ambient allow (ratified 2026-09-10). Veto possible.
- I stamped retirement_keepcut sheet ruled (blanket, his words); water_art_candidates ruled (accept A); pit ladder + drawbridge sheets retired as in-game-only. I added Alien Worlds x2 to the SHIP list (`1f6930706`).
- I changed RUT_FeverWood/RUT_Greentide BiomeDef workerClass to our own RM_ workers (the ReGrowth/CypreJungle classes did not exist).
- Owner said he told BENCH (not me) on many sheet rulings: BENCH is enacting facings_regen_picks and picks_dessicated; do not enact those here.

## What is half-done, and where it stops
- `BIOME_DEFNAME_MIGRATION_WAVE_1` and Wave 4 / Alien Worlds SHIP edit — built, undeployed; NEXT: with the game down and the bridge held, run deploy_custom_mods.py dry run then --apply for Biomes composite, FlowWorks, Pyrelands, UtinniPatches (and CreatureBehaviors, GimmeSomeSlack, Ninefold, EnvironmentalHazards, Armoury DLLs rebuilt tonight), then the Wave 4 324-mod list.
- `WATER_ART_CANDIDATES_BUILD_WHAT_HE_APPROVED` — filed, option A accepted on all four mocks; NEXT: build each A as real FlowWorks terrain art/defs.
- `FLOWWORKS_RESET_BUILD_TWELVE_SCREENS_MISSING` — filed; NEXT: add a shared reset helper and section lists to the 12 unreset FlowWorks screens.
- `ROT_WOUNDLINK_FIX_DROPPED_AT_THE_DOOR` — built (69905fd71), needs def read + quicktest; NEXT: run it at the next bridge sitting.
- Webwork urraveth_remains + traction_lance script chains (01bfb1a21, 670943878) — untested live; NEXT: deploy and run both chains at the next bridge sitting.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — 107 XML left DIRTY by design (heat ruling conflicts, dead retired-donor patches, huge generated files); NEXT: decide the dead-patch deletions (dead_patches.md) with him, then the Absorbed_* 'do NOT deploy' header question.
- required-checks manifest `script_sha` entries stale for touched validation.py files — NEXT: refresh them with required_checks.py (it hung once under a helper: run it alone).
- `RAIL_LADDER` / ladder and drawbridge art — BENCH has the in-game look; NEXT: nothing here.

## Traps learned
- FlowWorks C# SelfTest from the staged build folder always shows 14 false FAILs; run from the repo's bin/Release/net8.0. (filed: lessons)
- gen_pawnkind_roster was stripping 40 MayRequire guards from committed JawaFactionRoster.xml on every run (fixed f20d4c0b1); other generators overwrote decisions on an unreadable decisions file (fixed, see review_E notes). (see: commits 68bebc07a, f20d4c0b1)
- A DLL conflict blocks ./publish when BENCH commits a FlowWorks DLL under a helper: rebuild on origin/main, never hard reset. (see: review_D/H progress notes in seat-tmp)
- `rimflow next --seat OWNER` takes a lease for the owner seat as a side effect; release was refused for me, so I reverted the ledger line. (see: this session)

## Commits

```
8e1515bd8 RUT_FeverWood/Greentide twins: workerClass repointed to shipped RM_ workers (donor classes absent; matches Miasma/Forge/Sump twins)
b268922c9 code_review shard: XML review S batch 2 (42 files read or structurally verified; header fixes in 3aa6a572f)
3aa6a572f XML review S: stale header/comment fixes (AB_ terrain header, Terrorworm comments, art-pending notes)
4532bc6d8 code_review shard: XML review S batch 1 (Absorbed_KotorCore/VEF regen+diff, FloraStatAdj regen, SWBestiary races, biome frozen twins) Absorbed_* clean marks: generator regenerated in a sandbox; every committed delta (RSW_Durasteel retarget, cut-door/workbench refs) read.
e59562369 XML review S: stale header claims (donor-still-bare refs now ported, Tusk group is Core not Alpha Animals, retired Terrorworm/AB weather, CrackedLands op notes) Header text only; no def values changed.
d5528486c Restore lost owner-ruled values: RSW_Gutkurr/RSW_Wraid MoveSpeed 4.4; MechCluster allowedBiomes Rust Cathedral + Forge twins
713f9667f code_review shard: XML review batch 5 (SWBestiary races, Armoury absorbed, small mods)
7355722f1 XML review: more stale header/About text (Boma tusk group is Core, SandLion art accepted, LongShade row counts, Falumpaset/Jamel meat refs)
45d3e1c88 XML review: stale About/header claims (retired donors still named active, ported sprites called placeholders, row counts)
2fe4e5f30 XML review: stale comments/About text (donor-era claims, art-now-exists, Vapaad gate, backstory counts 77->81)
95d2a45c1 XML review: AshStorms_Pyrelands comment still said the op layers AB_VolcanicAsh; it adds RM_VolcanicAsh
46208b6b8 code_review shard: XML review batch 4 (UtinniPatches small defs/patches, RimMandrake small mods)
0694179a1 XML review: ScariaOnsetArming header named retired AA_SpinedGow as a live filter entry
4f0b17ffd XML review: WildAnimals_BlueDesert/TheForge headers named retired AA_ donor rows as inline roster
bba209f68 XML review: ShokkweaveNestScatter FindMod named the composed-away 'RimMandrake: Webwork' (never loads); now Baroque Biomes
b111f6a9f code_review shard: XML review batch 3 (small mods, RimStarWars/RimUtinni About+patches)
bf1a07d73 XML review: TrophyCraft Items header and FungalSoil placeholder-art comment named retired donors
24483854f XML review: TrophyCraft About now names RM_Ollathrix (donor Wyyyschokk retired) and loads after biomes; Shokk dependency displayName
96c2fb689 XML review: Pyrinth About donor-retired, RustCathedral false alphabiomes-dependency text, duplicate empty <ingestible/> in Sump Dorvel/Skelver removed
84783f3de XML review batch 2: dead rotsporekit loadAfter and stale donor text removed from WeepingStones/Contagion About; 54 more XML marked clean
... 255 more: git log --oneline 482ea9c1b..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/biome_ffar/awaiting_pick_sheet_2026-10-19.decisions.json   review-sheet sidecar: his picks via the served sheet and/or my reviewStatus stamp (Transient, untracked-by-design except decisions)
 M Transient/biome_ffar/drawbridge_art_sheet_2026-10-20.decisions.json   review-sheet sidecar: his picks via the served sheet and/or my reviewStatus stamp (Transient, untracked-by-design except decisions)
 M Transient/biome_ffar/leaningscrub_open_rows_sheet_2026-10-18.decisions.json   review-sheet sidecar: his picks via the served sheet and/or my reviewStatus stamp (Transient, untracked-by-design except decisions)
 M Transient/biome_ffar/phase0_remaining_art_sheet_2026-10-16.decisions.json   review-sheet sidecar: his picks via the served sheet and/or my reviewStatus stamp (Transient, untracked-by-design except decisions)
 M Transient/biome_ffar/pit_ladder_hung_sheet_2026-10-16.decisions.json   review-sheet sidecar: his picks via the served sheet and/or my reviewStatus stamp (Transient, untracked-by-design except decisions)
 M Transient/biome_ffar/water_art_candidates_sheet_2026-10-17.decisions.json   review-sheet sidecar: his picks via the served sheet and/or my reviewStatus stamp (Transient, untracked-by-design except decisions)
 M Transient/modcheck/fixtures.json   pre-crash session leftovers, uncommitted; owner of the file decides
 M Transient/retirement_keepcut_sheet_2026-10-20.decisions.json   review-sheet sidecar: his picks via the served sheet and/or my reviewStatus stamp (Transient, untracked-by-design except decisions)
 M conversations/2026-10-22-0212-d1bc134c.md   conversation record, landed by the sweep
 M deployed/config/ModsConfig.before-tier-fw_gss_sitting.xml   pre-crash session leftovers, uncommitted; owner of the file decides
?? Transient/fw_scenes/live/S1_20261017T084726.txt   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_p00.png   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_p03.png   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_p10.png   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S1_p14.png   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   pre-crash FlowWorks scene captures (Transient, unpinned, ~14-day shelf)
... 157 more uncommitted paths (by top-level dir: Transient 153, deployed 3, src 1): git status --short
```

