# Lantern Deeps sheet close — progress 2026-10-05 (BENCH helper)

Owner: "Finished lantern deep sheet". Decisions: `Transient/biome_ffar/lanterndeeps_sheet_2026-10-05.decisions.json` (biome RM_LanternDeeps), 39 rows.

## Rulings read (group) — DONE
Raw decisions committed b933de948; 28 rows carry an owner `at` (03:38-03:45Z). Sheet A columns of the RM_ and RSW_ rows of
the eight BMT residents are BYTE-IDENTICAL (same shas): the RSW_ "keep A" picks are the pictures the RM_ defs already draw.
## Ingest (stamp ruled, art.py ingest) — pending
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
## Installs — pending
## Jobs queued — pending
## Items filed — pending
## Validation — pending
## Commits — pending
