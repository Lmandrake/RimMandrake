## spec
`mandrake.rm.biomes` (the unified biome mod, `RimMandrake.Biomes`) crashes RimWorld's
implied-corpse-def generation with a `NullReferenceException` in
`RimWorld.ThingDefGenerator_Corpses.CalculateMarketValue` (`raceDef.race` or a
`butcherProducts[i].thingDef` entry null) whenever it loads WITHOUT its full
owner-verified dependency set. RimWorld's own corrupted-mods recovery
("Caught exception while loading play data but there are active mods other
than Core. Resetting mods config and trying again.") then silently drops
**every** active non-Core/non-DLC mod and continues — so the resulting
session looks superficially healthy (a map generates, colonists spawn) while
**none** of our content is actually loaded. `jawa/get_defs` and
`rimworld/spawn_thing` both then report "not found"/"unknown ThingDef" for
literally every custom def, which reads exactly like a bridge-tooling
failure rather than what it actually is.

MEASURED 2026-09-29 (TERMINALBIOMES_REVIEW_FIXES_1 live-proof attempt), twice,
on two different mod lists:
1. `modset_builder.py --tier baroque_wave0` (13 mods: Core+5 DLC, Harmony,
   RimBridgeServer, VFE Core, Alpha Biomes, mandrake.rm.flowworks,
   mandrake.rm.luminouspigment, mandrake.rm.biomes) — crashed inside a VEF
   AnimalGenes postfix (`VEF.AnimalGenes.VEF_AnimalGenes_ThingDefGenerator_
   Corpses_GenerateCorpseDef_Patch:Postfix`) wrapping the same vanilla method.
2. A hand-trimmed 9-mod list (Core+5 DLC, Harmony, RimBridgeServer,
   mandrake.rm.biomes alone, no VEF/Alpha Biomes) — crashed in the SAME
   vanilla method with no mod postfix in the trace at all, meaning one of
   `mandrake.rm.biomes`'s own bundled race ThingDefs (or the biomes whose
   dependencies I removed) is the direct cause, not merely a VEF interaction.

Not diagnosed further this pass (out of scope for TERMINALBIOMES_REVIEW_
FIXES_1 — no TerminalBiomes file is implicated) but the root cause is very
likely a `butcherProducts` or `race.meatDef`/`race.leatherDef` cross-reference
in one of the ~29 bundled biomes that does not resolve when a MayRequire'd
donor mod (VEF, Alpha Biomes, SWBestiary, etc.) is absent from the list —
same failure family as `PATCH_MAYREQUIRE_GUARD_INERT_1` and the ModsConfig
reset documented in CLAUDE.md's "engine facts" section, but hitting implied
corpse-def generation instead of a patch operation.

## why this matters
`baroque_wave0` is the documented "fast single-mod re-check for future
changes to any folded biome's content" — it is supposed to be the safe,
cheap way to live-verify a change to any bundled biome. **It is currently
broken and produces a false-clean quicktest**, because the corrupted-mods
recovery hides the crash instead of surfacing it: no error dialog, no bridge
failure, just every custom def silently absent. The owner's real ~613-630
mod full list is unaffected (TerminalBiomes and its siblings load fine
there per existing shipped-content evidence) — this is specific to the
trimmed-tier dependency closure, not a defect that reaches players.

## criteria
- [ ] Identify which bundled biome's race ThingDef (or `butcherProducts`
      entry) NREs `ThingDefGenerator_Corpses.CalculateMarketValue` when VEF/
      Alpha Biomes/SWBestiary are absent — bisect by biome subfolder, or read
      the full stack + a debugger-style dump of `raceDef` if the log ever
      names one.
- [ ] Fix (guard the reference, or correct `baroque_wave0`'s dependency
      closure to include whatever donor mod that race def actually needs).
- [ ] Re-verify `baroque_wave0` loads clean (no "Caught exception while
      loading play data" line in Player.log) and `jawa/get_defs` resolves a
      known def from at least 3 different bundled biomes.
