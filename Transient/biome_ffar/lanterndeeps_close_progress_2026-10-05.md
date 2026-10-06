# Lantern Deeps sheet close — progress 2026-10-05 (BENCH helper)

Owner: "Finished lantern deep sheet". Decisions: `Transient/biome_ffar/lanterndeeps_sheet_2026-10-05.decisions.json` (biome RM_LanternDeeps), 39 rows.

## Rulings read (group) — DONE
Raw decisions committed b933de948; 28 rows carry an owner `at` (03:38-03:45Z). Sheet A columns of the RM_ and RSW_ rows of
the eight BMT residents are BYTE-IDENTICAL (same shas): the RSW_ "keep A" picks are the pictures the RM_ defs already draw.
## Ingest (stamp ruled, art.py ingest) — DONE
reviewStatus stamped ruled. `art.py ingest`: 22 rulings, 23 purges, 0 refused, 11 untouched, 0 unresolved.
req 9 (note verbatim): the 15 eye jobs target RM_ defs whose own sheet row is the CUT row ("cut dont need") because his
keep-with-note sits on the RSW_ row of the same creature. Checked with ingest.check_redo_jobs against the RSW_ rows: clean.
ingest ran with --redo-jobs on the other 20 rows (blinker + plants), which are also clean.
## Cuts — DONE
No RUT_ twin exists for this biome (Q6 moved the whole def up to RM_LanternDeeps), so the cuts are RM_LanternDeeps only.
- REMOVED entirely (nothing else casts or references them): RM_BovineBeetle (grabber), RM_GlowSlug (glowbulb),
  RM_ShatterjawBeetle + their 31-def port closure (larvae, eggs, gastropod meat/leather, bodies, sounds, support);
  RM_Chiller (ThingDef + PawnKindDef) with its C# (RM_CompHeatPusherGated, "Chillers cool the room" setting).
  port_fauna.py SEEDS now 5; the generator re-ran (1494 def lines out, 22 PNGs retired through the ledger).
  MapComponent_LanternDeepDarkness no longer names RM_ShatterjawBeetle; DLL rebuilt (winbuild).
- UNCAST only: RM_OsskBramble (still referenced by ExplosiveGrowth's roster and GenStep_DeepFloraGate).
- RSW_BovineBeetle / RSW_GlowSlug / RSW_ShatterjawBeetle: were never cast in RM_LanternDeeps; left in SWBestiary
  (RSW_GlowSlug is still in frozen RUT_FeverWood; RSW_BovineBeetle pinned by AnimalTolerances_Ashkarr). Scoped cut: no edit.
- TRAP hit and fixed: port_fauna.py rmtree'd all of Defs/Fauna and its TextureWriter.sync retired the whole
  Textures/.../Fauna root, which now also holds hand-authored Hydrocarbon/Crystal/OrunGhal art. The run retired 42 of
  those; all restored byte-exact from the art store and the 42 bogus retire events dropped before commit. Generator now
  deletes only its own RM_LanternDeeps_Fauna_*.xml and syncs only the subtrees it writes.
- validation.py: chiller dropped from wave1; residents chain now five, and asserts the cut kinds are absent.
## Tier moves (RSW_ -> RM_) — DONE (already in place)
RSW_FacetMothLarvae, RSW_Megapleura, RSW_MossBeetleLarvae, RSW_BloodropMoth, RSW_Gembug: the RM-tier creature already exists
as RM_FacetMothLarvae / RM_Megapleura / RM_MossBeetleLarvae / RM_BloodropMoth / RM_Gembug (LANTERNDEEPS_FAUNA_TIER_PORT_BUILD_1,
aeaa3caf0), cast inline in RM_LanternDeeps, franchise-free text, drawing the identical picture he kept. So the moved creature
holds the RM_ defName and the "cut" RM_ rows of the three are NOT removed (cutting them would cut the creature he kept).
Nothing to repoint: no cast/patch names the RSW_ five inside the RM tier. Retiring the RSW_ originals is filed (see Items).
## Installs — DONE (3, all `art.py install --ruling`, all placeholder_detect `real`)
- RM_DeepMycelium E -> Plant/Mycelium/A.png (replaces the A he passed over; unseen B/C stay).
- RM_ThrakkCap variants A,B: A already live; B -> Plant/ThrakkCap/C.png (unseen B.png kept).
- RM_Lanternstone_Sowable variants A,B,C: A (B.png) and B (C.png) already live; C -> Crystals/LanternstoneMedium/A.png.
  This folder is shared with the natural medium lanternstone, which gains the variant too.
- His other A picks (KuvraSpout etc.) are the live pictures already: nothing to install.
## Jobs queued — DONE (36 jobs from 35 rows), `Transient/biome_ffar/lanterndeeps_redo_jobs_2026-10-05.json`
- 15 eye repaints: one edit per facing of the live picture, using `reference` = art-store copy (no artsrc exists for
  these pictures, so derive_from was impossible). Drinker/soulchime/megapleura/moss grub: remove eyes. Gembug (Blue): pale blue gems.
- 3 blinker: east derive_from RM_Blinker_east (three radiating arms, legless, clumsy); north/south derive from the new east.
- 18 plant variants (b, c), 9 plants: DeepMycelium derive_from gapall_RM_DeepMycelium_v1; the rest carry the pick as
  canon_reference, because the live pictures are tinted and have no artsrc.
No facing words in any prompt or register.
## Items filed — DONE
- LANTERNDEEPS_SHEET_ART_REDO_1 (FOUNDRY): collect and install the 36 renders, plus the Gembug Green/Red/Yellow follow-up.
- LANTERNDEEPS_RSW_ORIGINALS_RETIRE_1 (BENCH, needs owner): delete or keep the RSW_ originals that port_fauna.py sources.
## Validation — DONE
validate_patch on LanternDeeps Defs + Patches: 41 files, 0 errors (19 advisory warnings). winbuild LanternDeeps: 0 warnings/0 errors.
art guard worktree: 0 unledgered texture changes. run_selftests 185/189. The 4 failures are not from this work:
selftest_art, ledger_lint and tool_metadata (failing before, see the Abyss record), and utinnipatches_dump
(RUT_Muddal/RUT_Thuum labels drifted from the dump).
## Commits
b933de948 raw decisions; cuts commit; ingest/installs/jobs commit (see git log).
