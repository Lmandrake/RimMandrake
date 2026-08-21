## spec
_not recorded in the source queue_

## verify
_not recorded in the source queue_

## criteria
_not recorded in the source queue_

## notes
⛔ **Folded into `BLACKSTAR_NEVER_GENERATES_1` (`queue/BUILD.md`), 2026-08-20.** My
original text named `AM_EnemyPirate` as the missing vessel; REP had already repointed the
source to vanilla `Pirate` while I was measuring, so that half is done and must not be
redone.
🔴 **BUT DO NOT RUN THE RE-IMPORT YET. One thing I found is not in that item and it
would waste the run:**
**`Pirate` IS NOT IN THE LIVE WORLD EITHER.** Measured in the 08:36 autosave:
`<def>Pirate</def>` appears **0** times, `<def>PirateWaster</def>` **0** times.
`BLACKSTAR_NEVER_GENERATES_1` says the importer *"refuses the WHOLE import if any faction
is unresolvable"* — so a re-import against the repointed CSV could now fail **all 72
rows**, where before it merely skipped 4.
⚠️ REP's precondition check was sound but aimed at a different artifact: `world/
WORLDMAP_gen.rws` does contain `<def>Pirate</def>`. **The world that is loaded is not that
file.** Check the world you are about to import into, not a world on disk.
🔑 **AND THE ROOT CAUSE, which explains why no amount of def patching fixes this:**
Biotech's `PirateWaster` declares `replacesFaction: Pirate` with
`requiredCountAtGameStart: 1`, and `FactionGenerator.InitializeFactions` **skips any def
another required faction replaces**. Vanilla `Pirate` is therefore never generated at all
while Biotech is active. And `requiredCountAtGameStart` is read **only at worldgen** —
there is no load-time top-up except a hardcoded list of five vanilla factions — so it
cannot arrive later on its own.
⇒ **The faction has to be CREATED, not configured.**
✅ **THE TOOL NOW EXISTS: `jawa/faction_create`.** Built 2026-08-20, waiting on the same
game-down deploy as everything else in `INHABITED_DLL_FIX_AT_SHUTDOWN_1` — expect **115**
`jawa/` tools afterwards, not 114. It wraps
`FactionGenerator.CreateFactionAndAddToManager`, which also wires relations with every
existing faction and recaches the manager, so nothing else is owed.
**THE ORDER, once it is deployed:**
  1. `jawa/faction_create` with `defName=Pirate` — ⚠️ it defaults to `dryRun=true`; read
     the plan, which will also report `displacedBy: ["PirateWaster"]` telling you WHY it
     was missing, then re-run with `dryRun=false`.
  2. `jawa/faction_name_set` `action=clear` — the new faction arrives wearing a
     GENERATED name, because `Pirate` has no `fixedName`. Clearing makes it read
     **"Blackstar Company"**, its def label.
  3. ONLY THEN re-run `world_settlements_import`. All 72 rows should land.
  4. **SAVE.** A created faction lives on the world object and is lost otherwise.
⚠️ This repairs THIS world. A future worldgen would lose `Pirate` again to Biotech —
that half is `PIRATE_REPLACED_BY_BIOTECH_1` in `queue/DECIDE.md` and is not yours.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

superseded — the live-world warning above is the part that is still live
