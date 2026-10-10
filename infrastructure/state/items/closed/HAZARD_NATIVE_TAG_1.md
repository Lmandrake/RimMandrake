# HAZARD_NATIVE_TAG_1 — TB-1/X-4: One "born here" tag: a creature names the hazards it is native to and HazardTargeting.Affects honours it everywhere (steam, steam devil, boiling water, current, hydrocarbon)

## spec

Filed from `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row TB-1/X-4 (belt hygiene pass 2 2026-10-09; items/ live+closed and src/ re-checked: not filed, not built). Scope: The fix-now half of TB-1 is already in src (RM_ScaldWalker is in the immuneThingDefs of RUT_ScaldExposure, RUT_ScaldSteamCarrier and RM_SteamDevil). Remaining: one generic extension read by EnvironmentalHazards HazardTargeting.Affects, replacing the three hand-kept name lists and RM_ChannelNativeExtension / RM_HydrocarbonNativeExtension / RM_RiverNativeExtension; a check that every Scald roster species carries it. Fits BIOME_MOD_UNIFICATION_1. Re-measure the three lists before editing.

The row:

| TB-1 | The Scald's big grazer (the iridesce) gets scalded by the steam and the steam devils on its own home floor. Fix it now, then make "native of the Scald" ONE tag on the creature that the steam, the steam devil and the boiling water all read, instead of three hand-kept name lists. Add a check that every species on the Scald roster carries it. | EnvironmentalHazards `HazardTargeting.Affects` reads a native tag | S–M | low | TerminalBiomes, EnvironmentalHazards | `RM_ScaldWalker` has the water half (`RM_OrganicScaldNative`, `RM_ScaldWalker.xml:69`) but is absent from `immuneThingDefs` in `RUT_ScaldExposure.xml:133`, `RUT_ScaldSteamCarrier.xml:54`, `RM_SteamDevil.xml:64` (whose own comment says "any future Scald native goes in all three"). Precedent tags exist: `RM_ChannelNativeExtension`, `RM_HydrocarbonNativeExtension`, `RM_RiverNativeExtension`. No item (index grep native/immun: none). |

| X-4 | **One "born here" tag for the whole planet.** A single creature tag names the hazards it is native to (steam, boiling water, current, hydrocarbon). The hazard code honours it everywhere, replacing three separate per-biome tags and the hand-kept immunity name lists. | one generic extension, read by `HazardTargeting.Affects` | M | low | EnvironmentalHazards, TerminalBiomes, BlueDesert, FlowWorks | `RM_ChannelNativeExtension`, `RM_HydrocarbonNativeExtension`, `RM_RiverNativeExtension` all exist. Fits BIOME_MOD_UNIFICATION_1. TB-1 is the first, urgent case |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; PatchApplier for any Harmony.

## verify

- Offline: EnvironmentalHazards and TerminalBiomes build; a check lists every Scald roster species and fails on one without the tag; the three name lists are gone.
