# EMPIRE_WHITELIST_OVERRIDDEN_1 — Empire's permanentEnemyToEveryoneExcept still whitelists the player

Split from `EMPIRE_RAID_QUICKTEST_1`, 2026-08-29. Full evidence there; summary here.

## spec
`GalacticEmpire.xml`'s `PatchOperationReplace` on
`/Defs/FactionDef[defName="Empire"]/permanentEnemyToEveryoneExcept` deliberately DROPS
`PlayerColony`/`PlayerTribe` from the exception list (the comment names this as the entire
mechanism that keeps Empire hostile). Live, `jawa/get_defs FactionDef/Empire
permanentEnemyToEveryoneExcept` (584-mod set, `OFFICIAL-2026-08-29`) returns 24 entries
INCLUDING `PlayerColony` and `PlayerTribe`, plus a dozen other mods' player-faction defNames
never mentioned in our patch. `validate_patch.py --live` confirms our own patch's xpath
matches correctly (every operation: `1 match(es)`), so this is not our patch failing to fire —
something else, loading after `mandrake.jawa.patches` (ModsConfig line 585), re-adds the
excluded entries.

## 2026-08-29 (FOUNDRY): correction to my own earlier reasoning, and 69 candidates cleared

🔴 **`validate_patch.py`'s "1 match(es)" does NOT prove our patch wins — corrected.** It
confirms the xpath is well-formed and matches a real node in the RAW, unpatched
`Royalty: Faction_Empire.xml` (an xpath-validity check), not that our `Replace` is the LAST
write in the full 584-mod patch application order. I read this as "our patch fires and is
final" earlier; it only proves the first half. Deployment was also checked and is not the
answer: `diff` between `src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml` and the deployed
copy under `Mods/Jawa_Patches/Patches/` is byte-identical.

**Exhaustively grepped 101 mods touching `permanentEnemyToEveryoneExcept` anywhere in the
1256-mod Workshop folder** → 69 of those also mention "Empire" → **zero of the 69 contain the
literal string `PlayerColony` or `PlayerTribe`.** The two most plausibly-named suspects by
filename (`empirehostileptach.xml`, `Patch_EmpireGoodwill.xml`) were read in full: both only
`PatchOperationAdd` a SINGLE unrelated defName each (`pphhyy_Demigryph_DemigryphKnights` and
`PlayerColonyBoS`/`PlayerColonyEnc` respectively) — neither touches vanilla `PlayerColony`/
`PlayerTribe` at all, and an Add cannot un-remove what a later Replace removed regardless.

**No XML file in any active mod contains the two specific strings that are reappearing.** This
rules out a straightforward "mod B's patch runs after mod A's and wins" explanation entirely.
The remaining live entries — `BS_PlayerColonyXenoPlus`, `VFEI2_PlayerOutpost`, `AM_PlayerColony`,
`VFEP_PlayerPirate`, `OuterRim_RogueDroidColony`, `OuterRim_EmpirePlayerFaction`,
`OuterRim_RebelPlayerFaction`, etc. — have the SHAPE of a compatibility FRAMEWORK
programmatically appending every active alternate-start mod's player-faction def to every
`permanentEnemy`/`permanentEnemyToEveryoneExcept`-carrying `FactionDef` via C# (likely a
`[StaticConstructorOnStartup]` pass, not XML), which would also explain vanilla `PlayerColony`/
`PlayerTribe` being restored if that same pass treats "the vanilla player factions" as always-
implied rather than reading them off our patched list. **Not confirmed — hypothesis only.**

## verify
Needs either (a) a live Harmony patch inventory naming what runs on `FactionDef`/`Faction`
post-load, or (b) a bisect: swap to the 13-mod minimal list plus Jawa_Patches plus Outer Rim
only, re-check `permanentEnemyToEveryoneExcept`, then add back mod groups until it reappears.

**(a) is no longer blocked on a missing tool, 2026-08-29.** `jawa/harmony_patches` — built for
`WILD_ANIMALS_PADDED_LISTS_1`, same capability gap this item names — is written, compiled
clean (`833dd0d8`), UNDEPLOYED. Once deployed: `jawa/harmony_patches {typeName: "FactionDef"}`
(and try `Faction` too — the framework hypothesis above suggests a per-instance write, which
could patch either the def-loading path or a runtime `Faction` method). Still needs a
game-down deploy window; still genuinely blocked on that, not on tooling.

## criteria
- [ ] The interloping mechanism named — narrowed to "likely a C# compatibility framework, not
      an XML patch" but not confirmed or named.
- [ ] A fix decided: reorder load, patch the interloper, or make Jawa's own hostility check
      NOT rely on `permanentEnemyToEveryoneExcept` at all (e.g. seed the relation directly via
      a companion tool or scenario part at world-gen) — owner's call once the mechanism is named.
- [ ] Live re-check: `jawa/get_defs FactionDef/Empire permanentEnemyToEveryoneExcept` excludes
      PlayerColony/PlayerTribe, and a fresh relation seed shows Empire Hostile to the player.

## 2026-08-30 (FOUNDRY) — mechanism found with `jawa/harmony_patches`, live, 585 mods

`jawa/harmony_patches` is now DEPLOYED and answers. Run against `FactionDef`, `Faction`,
`FactionGenerator`, `FactionManager`, `DefGenerator`, `DirectXmlLoader`, `LoadedModManager`
and `XmlInheritance` at the main menu (defs and Harmony patches are both in place before
any save loads).

### ⭐ The decisive hit — the whitelist is not what decides hostility any more

    RimWorld.FactionDef.PermanentlyHostileTo
      postfix  SWCP.Core.Patches.FactionDef_PermanentlyHostileTo_Postfix   [SWCP_Core]

and, from `vendor/mod_sources/SWCP_Core_decompiled/SWCP.Core/Patches.cs`:

```csharp
public static void FactionDef_PermanentlyHostileTo_Postfix(
    FactionDef otherFactionDef, FactionDef __instance, ref bool __result)
{
    if (!__result)
        __result = ((Def)__instance)
            .GetModExtension<ModExtension_FactionPermanentlyHostileTo>()
            ?.FactionIsHostileTo(otherFactionDef) ?? false;
}
```

`ModExtension_FactionPermanentlyHostileTo` is one field, `List<FactionDef>
hostileFactionDefs`, and `FactionIsHostileTo(other)` is `hostileFactionDefs.Contains(other)`.
SWCP postfixes **three** methods in the same family, all live:

    FactionDef.PermanentlyHostileTo                       -> the extension can force TRUE
    GoodwillSituationWorker_PermanentEnemy.ArePermanentEnemies -> same, per Faction pair
    Faction.CanChangeGoodwillFor                          -> locks goodwill when hostile
    Faction.TryMakeInitialRelationsWith .. GetInitialGoodwill  -> prefix, forces -100

🔑 **This is a purely ADDITIVE route that cannot lose a patch race.** Every postfix above
fires only when the vanilla answer was already `false`, and nothing else in the mod set
writes that mod extension. Putting `PlayerColony`/`PlayerTribe` in Empire's
`hostileFactionDefs` makes `Empire.PermanentlyHostileTo(PlayerColony)` return true
**regardless of what `permanentEnemyToEveryoneExcept` ends up containing** — which is the
outcome this item wants, reached without having to win the whitelist argument at all.

### The whitelist itself: our patch DOES win, and the extras are appended afterwards
The live 24-entry list opens with our patch's **exact 12 entries in our exact order**
(`Jawa_HuttCartel` … `TradersGuild`), then appends `PlayerColony`, `PlayerTribe`,
`BS_PlayerTribeXenoPlus`, `BS_PlayerColonyXenoPlus`, `VFEI2_PlayerOutpost`, `VFET_WildMen`,
`VQE_NewVaultPlayerFaction`, `AM_PlayerColony`, `VFEP_PlayerPirate`, `BS_JotunPlayerColony`,
`OuterRim_RogueDroidColony`, `OuterRim_EmpirePlayerFaction`, `OuterRim_RebelPlayerFaction`.

⭐ **The ORDER is the evidence, and it corrects the 2026-08-29 framing.** Our `Replace` is
not being beaten — it lands, and the list it produced survives intact as the prefix. Every
appended entry is a `isPlayer=true` FactionDef, so a post-load C# pass appends "all player
factions", exactly the framework shape hypothesised before. The two XML candidates that
touch this xpath were read and are both harmless prefix-preserving `Add`s:
`VFE-Insectoids2/1.6/Patches/Royalty.xml` adds `VFEI2_PlayerOutpost` only, and
`CaravanAdventures`' `StoryUtility.cs` adds only sacrilegHunters/mechanoids at runtime.

## criteria
- [x] The interloping mechanism named — **`SWCP.Core.Patches.FactionDef_PermanentlyHostileTo_Postfix`
      (assembly `SWCP_Core`) is what actually decides this**, via
      `ModExtension_FactionPermanentlyHostileTo`; the whitelist no longer has the last word.
      (The separate cosmetic question of which mod appends the player factions to the list
      is now moot for hostility — our own entries are intact and the extras change nothing
      once the extension is present.)
- [ ] **A fix decided — OWNER'S CALL, and there is now a clean recommendation.** Add to
      `src/Jawa/Jawa_Patches/Patches/GalacticEmpire.xml`:

          <li Class="PatchOperationAdd">
            <xpath>/Defs/FactionDef[defName="Empire"]</xpath>
            <value>
              <modExtensions>
                <li Class="SWCP.Core.ModExtension_FactionPermanentlyHostileTo">
                  <hostileFactionDefs>
                    <li>PlayerColony</li>
                    <li>PlayerTribe</li>
                  </hostileFactionDefs>
                </li>
              </modExtensions>
            </value>
          </li>

      ⚠️ Gate it on SWCP being active (`PatchOperationFindMod`) — a `Class=` naming a type
      no loaded assembly has **discards the whole FactionDef silently**
      (`modextension-missing-type-discards-def`), which would delete the Empire outright.
      ⚠️ `Empire` may already declare `modExtensions`; if so this must be an Add INTO that
      list, not an Add of the list. Check before writing.
- [ ] Live re-check after the fix: Empire reads Hostile to the player from a fresh relation
      seed. (The whitelist half of the old criterion is retired — it will keep reading 24
      entries and that is now known to be harmless.)
