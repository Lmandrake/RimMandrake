# Biome-sprint kit art: guessed designs, 2026-10-16 (FOUNDRY helper)

Owner, `--owner-said`: *"Go ahead and queue all pending art"*. By card (kit art ahead of the sprint): *"Let me guess the
designs"*: the agent proposes a one-line design per piece, he vetoes later, and the rest is commissioned now. **Every line
below is an agent guess, not his ruling. Strike a line to veto it; the render then never installs.** Nothing here is
installed; renders land in `D:\Luke\dev\_artpipe\done\` and go on the S1 sheets before any `art.py install`.

Job file: `D:\Luke\dev\RimMandrake\design\RimMandrake\kit_art_jobs_2026-10-16.json` (priority 38-40, 21 jobs, item
`SPRINT_KIT_ART_SKETCH_BEFORE_THE_VETO`). Sprint scope: `design/RimMandrake/biome_sprint_kickoff_2026-10-15.md` §1.1-1.3.

## Commissioned (one-line designs to veto)

| piece | def (tier) | job id (facings, canvas) | the guessed design |
|---|---|---|---|
| Corroded filter rig (Cauldron ruin anchor, study source for the Filter-Works) | `RM_CorrodedFilterRig` (RM) | `kit_corrodedfilterrig_v1` (single, 512) | The `RM_FilterWorks` pressure vessel left to the forest for a lifetime: split riveted housing on a sagging salvage frame, cartridge breech rusted open with a rotted rack inside, intake pipes snapped off, purple-red crust and crystal fur, one dried green-amber stain under the dead outlet. |
| Oomo grudging shrine | `RUT_OomoGrudgingShrine` (RUT, Oomo is Utinni lore) | `kit_oomoshrine_v1` (single, 256) | A squat slate plinth with a cracked votive dish holding one carved, polished stone droplet; a small hooded Oomo idol on the back edge sits half-turned away, hem sagging damp: he came, and he sulks. Grey stone, no green-amber, condensate beading. |
| Wind vaporator | `RM_WindVaporator` (RM; the canon "moisture vaporator" name stays out) | `kit_windvaporator_v1` (single, 256x512, 1x1 footprint, height extends north) | A hand-built fog-comb: a slim mast of lashed scrap pipe rising from a squat pump housing, its upper half a vertical comb of fine wire tines strung between two bars, a drip lip and gutter feeding a sealed cistern drum at the base. Clean and working (Q8: no scar). |
| Fog water | `RM_FogWater` (RM) | `kit_fogwater_v1` (single, 256) | A stoppered clay-and-tin canteen jug, beaded with cold condensate, a twist of comb wire round the neck. |
| Calling-pyre ritual icon | `RM_Ritual_CallingPyre` (RM; also used by the issue and precepts) | `kit_callingpyre_icon_v1` (single, 256) | A flat white glyph: a ring of stakes all leaning one way, a flame rising from the ring's centre. Tinted by the game like vanilla ritual icons. |
| Calling-pyre stake ring (the found study source) | none yet; proposed `RM_CallingPyreRing` (RM) | `kit_callingpyre_ring_v1` (single, 512, 3x3) | A ring of nine charred fence stakes driven into scorched fuzz-ground, every stake leaning sunward with the wind, one stake carved with a band of notched script, ash drifted against their downwind sides. |
| Comb holds faction icon | `RM_Faction_CombHolds` (RM) | `kit_combholds_icon_v1` (single, 256) | A flat white glyph: a vertical comb of tines over a single falling water drop. |
| Comb-hold lean-to (camp kit) | none yet; proposed `RM_CombHoldLeanTo` (RM) | `kit_combhold_leanto_v1` (single, 512, 2x2) | A low wind-shaped shelter of grey-blue tarp and patched hide stretched over bent poles, back to the wind and weighted with stones, a small comb-mesh drip catcher at the front corner. Lived in: a rolled blanket, a hanging cup. |
| Comb-hold water cache (camp kit) | none yet; proposed `RM_CombHoldWaterCache` (RM) | `kit_combhold_watercache_v1` (single, 256, 1x1) | Three sealed cistern jugs of the fog-water kind, roped together under a weighted grey tarp corner on a pallet of scrap boards. |
| Smother blanket | `RM_SmotherBlanket` (RM) | `kit_smotherblanket_v1` (single, 256) | A folded slab of heavy, near-black felted venomvine fibre, tarred along one edge, stitched with coarse cord: the cloth that banks a claim. |
| Caudal Spring, worn | `RM_CaudalSpring` (RM) | `kit_caudalspring_v1` (east master, south and north derived, 256) | A segmented gristle tail grown from the base of the spine, folded under itself in tight coils like a compressed spring, ending in a flat pad; skin-tintable desaturated flesh. Replaces the Anomaly TentacleLimb stand-in. |
| Bellows, worn | `RM_Bellows` (RM) | `kit_bellows_v1` (east master, south and north derived, 256) | A translucent pink bladder bulging from one flank of the ribcage, a faint red fog swirling inside it, fine veins across its skin. Not skin-tinted. The hediff needs a render node added (def task). |
| Eyeburst, worn | `RM_Eyeburst` (RM) | `kit_eyeburst_v1` (east master, south and north derived, 128) | A wet cluster of about a dozen mismatched eyes, pink- and blue-irised, all sizes, some half-lidded, bulging where one eye was. Replaces the tinted vanilla BionicEye. |
| Contagion mulch | `RM_ContagionMulch` (RM) | `kit_contagionmulch_v1` (single, 256) | A small heap of dark clotted red-brown matter with a wet sheen, fibrous like spent compost, sterile and rich. |
| Draftprint | `RM_Draftprint` (RM) | `kit_draftprint_v1` (single, 256) | A scuffed data slate showing a glowing pale body-outline scan, its frame stained with dried red residue. |

## Skipped, and why

| what | why |
|---|---|
| Filter-Works building and cartridge | Already rendered (`done/RM_FilterWorks`, `done/RM_FilterCartridge`, 2026-09-29); no building def yet (waits on S0-9, the FlowWorks litres move). |
| Ruin kit wellhead, condenser stack, gas-tap scaffold, vent | Already rendered (`RM_CorrodedWellhead`, `RM_CorrodedCondenserStack`, `RM_GasTapScaffold`, `RM_CauldronVent`); wiring them into `RM_CompProperties_CauldronRuinKit` is a def task. |
| Corroded ruin shrine | `done/RM_CorrodedShrine` exists. The Utinni Oomo shrine above is a different, usable building. |
| Cauldron fleck overlays (2) and dew variants (5) | Rendered 2026-10-10 (`gap_RM_AssayFlecks_*`, `gap_RM_Dewfall_*`), not installed: `CAULDRON_FLECKS_FILL_SEVEN_STILL_BLANK` is an install and sheet task. |
| Wrecked wind vaporator (`RM_WindVaporatorWreck`) | Must be the same machine as the working one: queue it with `derive_from kit_windvaporator_v1` once that render lands. |
| Comb-hold apparel and headgear | The pawn kinds use vanilla apparel pools by design ("Pawns are human; no new art"); a distinct look needs new apparel defs, which is his call. |
| Half-made tree | Rendered and installed; three variants each exist (`contagion_HalfmadeTree_var1..3`, `..Blighted_var1..3`). What is owed is his pick. |
| Sunbeam projectile | The beam is the game's effect, not a sprite; low value. |
| Scavenger-clan camps | The Jawa race and camp art already exist (SW tier). |
| Seismograph | Cut by him. |

## Def follow-ups the art implies (not done here)

- `RM_WindVaporator`: texPath to the new art, `drawSize (1,2)`, `drawOffset (0,0,0.5)`.
- `RUT_OomoGrudgingShrine`: texPath to the new art, drop the AnimusStone tint.
- `RM_Bellows`: add a Spastic render node (breathing pulse, scale 0.9-1.1). `RM_CaudalSpring`: re-zero its east/west rotation offsets, then check live with him present.
- `RM_Eyeburst`: confirm the eye worker reads `_east/_north/_south` before installing three facings.
- New defs for the stake ring, lean-to and water cache, if he keeps them.
