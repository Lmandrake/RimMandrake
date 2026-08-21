## spec
In `src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml`:
**(1)** change the `permanentEnemy` operation from `true` to **`false`**.
🔴 **Do NOT merely delete it — set it false.** `FactionDef.PermanentlyHostileTo`
(`FactionDef.cs:463`) tests `if (permanentEnemy) return true;` FIRST and returns
before the list is read, so leaving it true keeps the whole list dead code.
**(2)** REPLACE `/Defs/FactionDef[defName="Empire"]/permanentEnemyToEveryoneExcept`
with exactly this list. ⚠️ It is a **whitelist of who is NOT a permanent enemy** —
anything absent is hostile:
```
Jawa_HuttCartel · Jawa_DeepwaterCompact · OutlanderCivil · TribeCivil · Pirate
Jawa_IndigenousTribes · Jawa_Junkers · Ancients
Beggars           MayRequire="Ludeon.RimWorld.Ideology"
ResearchExpedition MayRequire="Ludeon.RimWorld.Anomaly"
GravshipCrew      MayRequire="Ludeon.RimWorld.Odyssey"
TradersGuild      MayRequire="Ludeon.RimWorld.Odyssey"
```
⛔ **DELIBERATELY OMITTED — do not "helpfully" add them back:** `PlayerColony` and
`PlayerTribe` (this is what keeps the Empire permanently hostile to the player, the
owner's 2026-08-14 ruling), plus `Jawa_FreeDroidEnclaves`,
`Jawa_GeonosianFoundryHive`, `Jawa_WildsteamClan`, `Jawa_AscendantHelix`.
🪤 Keep the four DLC entries' `MayRequire` attributes — all four DLCs are active
here, but the attribute is correct and costs nothing.
⚠️ No `PatchOperationFindMod` wrapper anywhere in this file: Royalty is always
loaded on this stack.

## verify
`validate_patch.py --defs` clean; the live def reads `permanentEnemy false` and a
12-entry `permanentEnemyToEveryoneExcept`; neither player faction appears in it.

## criteria
at the owner's worldgen run the Empire generates permanently hostile to the player
and to the four omitted factions, and NOT permanently hostile to the Hutt Cartel —
confirmable on the faction relations screen without loading a map.

## notes
**from:** DECIDE, 2026-08-20, on the owner's ruling *"Option (b) please."* Full reasoning
and the design rationale for every entry: `design/Jawa/worldbuilding/EMPIRE_GAP_AUDIT.md` §2.
⚠️ **Worldgen-critical — faction relations are set at world creation.**

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

done 2026-08-20. Both ops written to
`src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml` and deployed.
verify output: `validate_patch.py --defs` against the 578-mod load set —
  `OK - 0 errors, 0 warning(s)`, and **every one of the 15 ops reports
  `1 match(es)`**, including the new `permanentEnemy` Add and the
  `permanentEnemyToEveryoneExcept` Replace.
✅ The spec's Replace-vs-Add call was right and I checked it rather than trusting
it: `permanentEnemyToEveryoneExcept` IS present on the shipped vessel
(`Data/Royalty/Defs/FactionDefs/Faction_Empire.xml:57`), so Replace is correct;
`permanentEnemy` is absent, so that one stays an Add.
✅ The shipped list carries `PlayerTribe` and `PlayerColony`. Dropping exactly
those two is what makes the Empire permanently hostile to the player — that is
the mechanism behind the 2026-08-14 ruling, and it is now commented in the file.
12 entries, neither player faction among them.

🔴 **WHAT THIS DOES AND DOES NOT DO TO THE WORLD THAT ALREADY EXISTS.** The item
is marked worldgen-critical, which is true but incomplete, and the difference
decides whether anyone should expect to see a change:
  ❌ **NOT retroactive.** `Faction.TryMakeInitialRelationsWith` opens
     `if (RelationWith(other, allowNull: true) == null)` — it sets goodwill ONCE,
     when two factions first meet. Existing relation values will not be
     recomputed, so the Empire's current standing with anyone is unchanged.
  ✅ **But it is LIVE from now on, and that is the half that matters.**
     `Faction.CanChangeGoodwillFor` (`Faction.cs:535`) reads
     `permanentEnemyToEveryoneExcept` **every time goodwill would change**. Under
     the old `permanentEnemy: true` every faction's goodwill with the Empire was
     frozen; now the twelve on the list can move and everyone else stays locked.
     `PermanentlyHostileTo` is likewise consulted live by at least eight quest
     roots, so quest eligibility changes immediately.
  ✅ And any faction CREATED later — see `BLACKSTAR_NEVER_GENERATES_1` — gets its
     initial relations under the new list.
⇒ The criteria's "at the owner's worldgen run" is the right test for the initial
VALUES. Do not read "no change on the relations screen today" as a failure.
