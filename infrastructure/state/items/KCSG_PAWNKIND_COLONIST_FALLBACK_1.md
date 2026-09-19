# A PawnKindDef silently falls back to vanilla Colonist — NOT a KCSG bug

> 🔴 **Corrected the same day it was filed.** This was first written as a KCSG
> defect because KCSG layouts were where it was seen. It is not. On the
> 2026-09-19 620-mod cold load it reproduced through the plain vanilla debug
> action `Actions\Spawn Pawn...\RSW_Jawa`, with no KCSG involved at all: six
> spawns, four generated as `RSW_Jawa` and **two came back as vanilla
> `Colonist`/`Baseliner`**, on the requested cells, in the right faction, with
> no error logged. So the substitution lives in `PawnGenerator`, and it affects
> every route that asks for one of our PawnKindDefs — raids, quests and
> faction rosters as much as dungeon layouts. Widen any fix accordingly.

## what was measured
FOUNDRY bridge wave 2, 2026-09-19, live 622-mod session, throwaway 250x250
`RUT_Desert` map. `jawa/kcsg_place structure RUT_Ashfall_Spire` placed three
times. The shipped layout carries exactly **five** pawn symbols
(`RUT_Symbol_HelixGrunt` x2, `..._HelixHeavy`, `..._HelixSpecialist`,
`..._HelixLeader`). Every placement filled all five cells with a spawned
Human — but the pawn's `kindDef` was the symbol's `pawnKindDef` only
**4 / 3 / 5** times:

| placement | kinds actually present |
|---|---|
| rect 170,170 | Grunt x2, Leader, Specialist, **+1 `Colonist`** |
| rect 20,20    | Heavy, Leader, Grunt, **+2 `Colonist`** |
| rect 20,110   | Grunt x2, Heavy, Specialist, Leader — all 5 correct |

## what it is NOT
- Not a layout bug: the symbol grid, the cell coordinates and the thing
  census (4 specimen cells, 1 console, 1 codes, 3 Tesla, 2 Railgun) are
  byte-identical across all three placements.
- Not a missing def: `PawnKindDef/RUT_Jawa_Helix_Heavy` resolves live, and
  `KCSG.SymbolDef/RUT_Symbol_HelixHeavy` reads back correct through
  `jawa/get_defs` (`pawnKindDef RUT_Jawa_Helix_Heavy`, `faction
  RUT_Jawa_AscendantHelix`, `numberToSpawn 1`).
- Not specific to one kind: the Heavy, the Specialist and a Grunt were each
  substituted in different placements.
- Not logged: `jawa/drain_log errorsOnly` shows zero lines naming Ashfall,
  Spire, KCSG, Helix or any of these defNames.

## the signature
The substituted pawn sits on the symbol's exact cell, carries the **right
faction** (Ascendant Helix) and **xenotype `Baseliner`** where the correct
pawns carry a faction xenotype (`RSW_RimMandrakeArkanian`,
`RSW_RimMandrakeKaminoan`). That is the shape of a `PawnGenerator` fallback
to `PawnKindDefOf.Colonist`, not of KCSG failing to read the symbol.

## why it matters beyond one dungeon
Every KCSG layout we ship stocks its guardians this way. A layout authored to
place a named boss can silently place a baseliner colonist instead, with the
right faction and no error — so **a per-defName pawn census of a KCSG layout
is not a deterministic check**, and any item that closes on "N pawns of kind
X appeared" has been reading a die roll.

## what to do
1. Read the generation path with RimSage (Desktop only): `SymbolResolver`
   for pawn symbols → whatever calls `PawnGenerator.GeneratePawn`, and find
   which `PawnGenerationRequest` failure re-requests `PawnKindDefOf.Colonist`.
   The faction-xenotype difference is the clue: `useFactionXenotypes` is
   true on all four Helix kinds, so a xenotype-resolution failure is the
   first suspect.
2. Then decide whether it is ours to fix (the kinds' own fields) or KCSG's.
   ⛔ Do not "fix" a layout on this finding — the layout is correct.

## criteria
- [x] The substitution's cause named from the engine source, not inferred.
- [x] A repeat test that says whether it is our PawnKindDefs or KCSG. — neither; see below.
- [ ] If ours: fixed, and 5 placements in a row give the intended 5 kinds. — mitigation shipped,
      live repeat-test not run (out of scope for this pass; see recipe below).

---

## ✅ ROOT-CAUSED 2026-09-19 (FOUNDRY) — it is `PawnGenerator`'s own world-pawn redress path colliding with a third-party Harmony patch. NOT KCSG, NOT a misconfigured FactionDef/PawnKindDef.

Full trace of 1.6 `Verse/PawnGenerator.cs` via RimSage (`read_csharp_symbol`,
`search_source`), method by method:

- `PawnGenerator.GeneratePawn(kindDef, faction, tile)` (the overload every plain
  caller uses — the vanilla debug "Spawn Pawn..." action, KCSG's pawn symbol,
  `SymbolResolver_SinglePawn`) builds a `PawnGenerationRequest` with
  **`forceGenerateNewPawn` left `false`** (its default).
- `GenerateOrRedressPawnInternal` — when `forceGenerateNewPawn` is false — rolls
  `Rand.Chance(ChanceToRedressAnyWorldPawn(request))` (`0.02 + 0.01·freeWorldPawns/10`,
  capped 0.8) and, on a hit, pulls an **existing pawn out of `Find.WorldPawns`**
  via `GetValidCandidatesToRedress`/`IsValidCandidateToRedress` instead of
  generating a fresh one. This is vanilla's own population-recycling mechanism
  (owner confirmed the family: *"substitutes humans from the colony's potential
  list… for a while at the beginning of a colony"*), not a bug by itself.
- `RedressPawn(pawn, request)` is then supposed to force the recycled pawn onto
  the requested kind: `pawn.ChangeKind(request.KindDef)` — `Verse/Pawn.cs:6094`,
  unconditional in vanilla (`if (kindDef != newKindDef) kindDef = newKindDef;`).
  **`RedressPawn` never touches genes/xenotype at all** (confirmed reading the
  full method body) — it only strips genes flagged `removeOnRedress`.
- Every other path in `PawnGenerator` (`TryGenerateNewPawnInternal`,
  `GenerateNewPawnInternal`, `GeneratePawn`, `ValidateAndFix`,
  `GenerateOrRedressPawnInternal`) sets or preserves `pawn.kindDef =
  request.KindDef` unconditionally, retries the SAME request up to 120 times on
  any validator failure, and returns `null` with a logged
  `"Pawn generation error… returning null"` on total failure — **there is no
  vanilla branch anywhere that answers a request for kind A with a pawn whose
  kindDef is B.**

⇒ **The only place a request for our kind can come back as vanilla `Colonist`
is a redressed world pawn whose `ChangeKind` call did not take.** Confirmed
locally: `mandrake.rut.flowworks`'s sibling item
`infrastructure/state/items/SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1.md` root-caused
this exact mechanism in 2026-08-27→09-02 for our OWN `jawa/spawn_pawn` bridge
tool (same trace, independently arrived at), named the standing suspect
**`AlienRace.HarmonyPatches.ChangeKindPrefix`** (HumanoidAlienRaces, workshop
`839005762`, confirmed present at `.../839005762/1.6/Assemblies/AlienRace.dll`)
by elimination of every other by-ref-capable pawn-gen patch in the load order
(`AlienRace` x2 other methods, `FactionLoadout`, `EBSGFramework`, `BigAndSmall`
— all ruled out by decompile), and shipped a LOCAL fix for that one tool
(`forceGenerateNewPawn: true`, bypassing redress entirely).

**What that sibling item's fix does NOT reach: everything else.** `jawa/spawn_pawn`
is the only call site we control. The vanilla debug action, KCSG's pawn symbol,
raid group generation, quest pawn generation and faction roster generation all
go through `PawnGenerator.GeneratePawn(kindDef, faction[, tile])` with
`forceGenerateNewPawn` false — so this item's finding (KCSG dungeons, and by the
same mechanism raids/quests/rosters) is the SAME defect on the paths that
sibling item explicitly could not fix.

### why it targets exactly our kinds
Not a xenotype misconfiguration. `RUT_Jawa_Helix_*` (and every other
`useFactionXenotypes: true` kind in the roster) is unremarkable —
`RUT_Jawa_AscendantHelix`'s `xenotypeSet` in
`src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaAscendantHelix.xml` sums to
~0.917 with the remainder correctly falling to `Baseliner` via
`PawnGenerator.XenotypesAvailableFor`'s own `num > 0f` top-up — vanilla behaviour,
not a bug. `useFactionXenotypes` is a *correlate*: it is what marks a kind as
one of our Humanlike-alien-race-flavoured kinds, which is exactly the population
`AlienRace.HarmonyPatches.ChangeKindPrefix` exists to intercept (it manages the
alien race's body/graphics/xenotype bookkeeping across a kind change). A plain
vanilla `Human`-race kind with no alien-race involvement never reaches that
prefix and never shows the symptom.

### the "signature" observation, fully explained
The item's original "signature" section (right faction + Baseliner xenotype
where a faction xenotype was expected) is now mechanistic, not inferred: the
redressed pawn IS the recycled world pawn, keeping its OWN pre-existing
xenotype (RedressPawn never re-rolls genes) while `SetFaction` correctly moves
it to the right faction. The wrong KIND riding along with it is the
`ChangeKindPrefix` failure on top.

## Is this ours to fix?
**Neither purely ours nor purely uncorrectable.** The root behaviour (vanilla
redress + a third-party mod's Harmony prefix on `Pawn.ChangeKind`) is a genuine
engine/mod-interaction limitation — we do not own `PawnGenerator` or
HumanoidAlienRaces, and there is no FactionDef/PawnKindDef field that avoids it.
But we DO own our own mod code, and the vanilla contract (`RedressPawn` must
leave `pawn.kindDef == request.KindDef`) is well-defined enough to restore by
force from outside, the same way `SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1` did
for one call site — this time on the shared engine method itself, so it covers
every caller instead of one tool.

## fix shipped this pass — mitigation, not a root fix
`src/RimStarWars/JawaRules/Source/JawaRules.cs`: new Harmony **Postfix** on
`PawnGenerator.RedressPawn` (`Patch_RedressPawn_ForceKind`), registered in
`JawaRulesMod`'s hand-resolved `Apply()` list (same fail-soft pattern as this
assembly's other four patches — a missing target logs one named error and
leaves the rest of the mod working). After the original method returns:
- if `pawn.kindDef != request.KindDef`, assigns the field **directly**
  (`pawn.kindDef = request.KindDef;`), bypassing `ChangeKind()` entirely —
  calling `ChangeKind` again would hit the exact same Harmony prefix that
  skipped it the first time, since Harmony patches apply per-call regardless
  of caller;
- if Biotech is active, the kind carries `useFactionXenotypes`, and the
  pawn's current xenotype does not match what `PawnGenerator
  .GetXenotypeForGeneratedPawn(request)` would have rolled, re-rolls it via
  `pawn.genes.SetXenotype(...)` — repairing the half of the symptom
  `RedressPawn` never touches even when `ChangeKind` succeeds;
- logs once (`Log.WarningOnce`, new hash `0x4A57A3`) naming the before/after
  kind, so a live session can grep for exactly when this fires.
Gated behind a new Mod Settings toggle, `pawnKindRedressFixEnabled` (default
**on** — the fix ships as the shipped behaviour, per this repo's Mod Settings
rule), in `RSW_JawaRulesSettings.cs`.

**Compiles clean**: `dotnet build JawaRules.csproj -c Release` via the
user-local SDK — 0 warnings, 0 errors,
`src/RimStarWars/JawaRules/Assemblies/JawaRules.dll` rebuilt and committed
alongside the source (this repo's existing convention for this assembly).
🔴 **Built, NOT deployed** — the live Mods folder is a separate copy
(`rimworld-deploy` skill); deploy is owed at the next game-down window,
`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaRules --apply`
(dry run first).

### what this fix does NOT do
- Does not stop the redress from happening (population recycling is preserved;
  only kind+xenotype correctness is enforced after the fact).
- Does not confirm `AlienRace.HarmonyPatches.ChangeKindPrefix` is the exact
  blocking prefix — that attribution is inherited from
  `SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1` and explicitly marked
  **UNPROVEN** there ("I did not establish that the prefix returns false"). This
  fix does not depend on which patch it is, since it repairs the *result*
  (`pawn.kindDef`/xenotype) rather than un-blocking the *call* — so it holds
  even if the true culprit turns out to be a different mod.
- Does not touch `jawa/spawn_pawn` (already fixed separately, `forceGenerateNewPawn:
  true`, deploy owed there too per that item).

## live repeat-test recipe for whoever verifies it (NOT run this pass — bridge untouched by design)
1. Deploy `JawaRules` (see above) at a game-down window, then a normal cold
   load or minimal-list quicktest with Biotech active.
2. Confirm the log shows `[RimMandrake.StarWars.JawaRules] pawnkind-redress-fix:
   armed;` at startup (proves the patch attached — `RedressPawn` is a `public
   static` method with a stable name, low inline risk, but check anyway per
   this repo's own inlining lesson).
3. `jawa/kcsg_place structure RUT_Ashfall_Spire` **5 times** (the item's own
   original criterion) on a throwaway map with a stocked Ascendant Helix world-pawn
   pool (spawn/generate several Helix-faction pawns first via
   `jawa/spawn_pawn` with `count` large enough to seed `Find.WorldPawns`, since
   the redress path only fires when candidates exist — an empty pool cannot
   exercise this at all, exactly as `SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1`
   measured its own rate decaying to 0% once a pool drained).
4. `jawa/list_pawns` (or equivalent) per placement: PASS is all 5 symbol cells
   showing `RUT_Jawa_Helix_Grunt`/`Heavy`/`Specialist`/`Leader` (2/1/1/1) with a
   faction xenotype, never `Colonist`/`Baseliner`, across all 5 placements.
5. If a `Colonist` still appears: grep the session's `Player.log` for the
   `pawnkind-redress-fix:` WarningOnce line. Present but the kind still wrong ⇒
   this patch fired but something re-overwrote `pawn.kindDef` afterward (a
   LOWER-priority Harmony postfix running after ours, or KCSG's own placement
   step) — a genuinely new finding, not a repeat of this one. Absent entirely ⇒
   the patch did not attach (log the startup line, or the redress path did not
   fire this run — increase sample size per the sibling item's rate-decay
   finding before concluding anything).

## why this item stays `doing`
The fix compiles and is reasoned from source, but per FOUNDRY ground rules for
this pass the bridge was deliberately not touched — the live repeat-test above
has not been run, `AlienRace.HarmonyPatches.ChangeKindPrefix` is still an
inherited, unproven attribution (though the fix does not depend on it), and the
deploy step is owed. Leave `doing` for whoever runs the recipe above.
