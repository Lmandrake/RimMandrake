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
- [x] Mod's real assembly/packageId identified from the live mod list, not guessed.
      `SWCP_Core.dll`, mod "Star Wars KotOR Resources and Materials",
      `guy762.MM.KotORCore`, loadOrder 575, at
      `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3254370945\1.6\Assemblies\`.
- [x] DLL decompiled; method signatures read, not guessed.
      `ilspycmd` 9.0.0.7889 (`ICSharpCode.Decompiler` 9.0.0.7889) — the pinned tool
      was broken (needed a dead net6.0 runtime); fixed by uninstalling and
      reinstalling with `--version 9.0.0.7889 --ignore-failed-sources` (later
      versions hit an unrelated `DotnetToolSettings.xml` install bug on this
      machine's SDK). All 5 DLLs in the mod's Assemblies folder decompiled to
      `vendor/mod_sources/<name>_decompiled/` (gitignored, derived, regenerable —
      not committed) to confirm which one actually holds the character system:
      SWCP_Core (108 files) has it; SWCPEnlist, SWCP_Currencies,
      SWCP_RimframeGrineerDoors, SWCP_Shuttles do not (grepped for
      pool/displac/roster/authored across all five — zero hits outside
      SWCP_Core, and none of those four words appear even there — the owner's
      debug-menu recollection ("Spawn authored character"/"Draw 3 from
      pool"/"Report displaced pool"/"Spawn roster") doesn't match any string in
      any of the five DLLs; the real category is `"SWCP: Characters"` with
      exactly 3 debug actions — GenerateCharacter, LogCharacters, LogRoles).
      The real mechanism: `CharacterDef : Def` (pawnKind/faction/xenotype +
      appearance/story/title/unique-item `definitions` + `roles`),
      `UniqueCharactersTracker : WorldComponent` — a per-CharacterDef SINGLETON
      pawn cache (`GetOrGenPawn`, generate-once-reuse-forever), and
      `CharacterRoleUtils`'s `RoleRegistry` (the exact "role registry" the
      owner's Player.log line names).
- [x] At least one genuinely new capability built (not a duplicate of spawn_pawn).
      Two tools, `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSwcpCharacterTools.cs`:
      `jawa/swcp_character_roster` (read-only; lists every authored CharacterDef
      plus, when a World is loaded, its live tracked state read from the
      tracker's own private `characters` field — never generates a pawn) and
      `jawa/swcp_character_spawn` (get-or-generate + place SWCP's SINGLETON
      character pawn, refuses to silently relocate one already spawned unless
      `forceRespawn=true`). Neither duplicates `jawa/spawn_pawn`, which always
      rolls a fresh generic pawn and has no concept of the mod's own
      one-pawn-per-authored-character identity.
- [x] Builds clean, no duplicate alias.
      `dotnet build -c Release` via `build.py --gm --apply`: 0 warnings, 0
      errors. Checked both new names against every existing `jawa/…` literal in
      the companion source first — no collision.
- [ ] Deployed and proven live.
      Deployed: `build.py --gm --apply` copied the built DLL to the game's
      `BridgeTools\JawaBench\` folder. **Not provable right now — the game is
      DOWN** (offline session, RimBridgeServer only discovers companions at its
      own startup) — owed on the next game-up window: confirm both tools appear
      in `--list-tools`, then run `jawa/swcp_character_roster` and
      `jawa/swcp_character_spawn` against a real SWCP-authored character.

--- history ---
