# SWCP_CHARACTERS_DECOMPILE_1 — decompile SWCP:Characters to build bridge tools

Filed 2026-08-29, FOUNDRY, at session end (context restart imminent). Found via the
owner's own live debug-menu screenshots: a category "SWCP:Characters" (likely "Star
Wars Character Project" or similar) with debug actions "Spawn Character", "Spawn
authored character", "Draw 3 from pool", "Report displaced pool", "Log Characters",
"Spawn roster". No vendored source exists for this mod in `vendor/mod_sources/` —
unlike KCSG/Rimefeller/DBH, this one is genuinely DLL-only here.

## Why this one specifically
Owner ruling, asked directly whether to invest the decompile effort: **"Yes,
decompile it."** Of everything found across this whole session's mod-debug-menu
sweep, this is the one most directly tied to the campaign's own core work —
character/pawnkind roster generation is what B45–B51 and the whole faction-slate
effort is about.

## Spec
1. Locate the mod's assembly in the live Mods folder (grep `ModsConfig.FULL.LATEST.xml`
   or the deployed mod list for the packageId behind "SWCP:Characters" first — do
   not guess the folder name).
2. Decompile the DLL (ILSpy or equivalent) to get real method signatures — same
   standard this whole session held to for every other mod: read source, never guess.
3. Identify which of "Spawn Character"/"Spawn authored character"/"Draw 3 from
   pool"/etc. map to genuinely new bridge capabilities not already covered by
   `jawa/spawn_pawn`/`spawn_batch` (a pawn-kind-generic spawn) — this mod likely
   has its own character ROSTER/POOL concept worth exposing specifically (which
   authored characters exist, which have been drawn/displaced), not just another
   spawn path.
4. Build via reflection, same pattern as `JawaBenchVehicleTools.cs`/
   `JawaBenchKcsgTools.cs` — the assembly must not be hard-referenced, so the
   companion still loads without this mod present.

## Verify
Standard bar: builds clean, signatures read from decompiled source (state which
tool decompiled it and from where), no duplicate alias, deployed and proven live
against a real SWCP-authored character.

## criteria
- [ ] Mod's real assembly/packageId identified from the live mod list, not guessed.
- [ ] DLL decompiled; method signatures read, not guessed.
- [ ] At least one genuinely new capability built (not a duplicate of spawn_pawn).
- [ ] Builds clean, no duplicate alias.
- [ ] Deployed and proven live.

--- history ---
