# BLACKSTAR_IN_DEFAULT_LIST_1 — the defs are clean, and seven of our factions are not on the screen

**CHECK, 2026-08-22 ~08:30 PDT. 578 mods.** Read off the running game with `jawa/get_defs`
and off the 2026-08-21 dump. ⚠️ **The Configure Factions page was NOT seen** — the main
menu's buttons are drawn in an `ImmediateWindow` that `get_ui_layout` does not decompose and
`get_screen_targets` returns empty there. Everything below is read from **the fields the
engine's own query uses**, which is stronger than a glance but is not a glance.

## The def half — 4 of 4 PASS

| check | reading |
|---|---|
| `PirateWaster.replacesFaction` absent | ✅ **None** |
| `PirateWaster.requiredCountAtGameStart` == 0 | ✅ **0** |
| `Pirate.label` == `Blackstar Company` | ✅ **Blackstar Company** |
| `Pirate.settlementGenerationWeight` == 0.6 | ✅ **0.6** — and not 1, so the item's warning about `PIRATE_VESSEL_RESTORED_1` holds |

`PirateWaster_Yield.xml` did what it said. `Pirate.requiredCountAtGameStart` is **1**, so
Blackstar is in the default list.

## The screen half — mixed, and the waster clause fails

`FactionGenerator.ConfigurableFactions` is, quoted from `OnlyOurFactions.xml`'s own header:

    from f in DefDatabase<FactionDef>.AllDefs where f.maxConfigurableAtWorldCreation > 0

| def | `maxConfigurableAtWorldCreation` | on the screen? | in the DEFAULT list? |
|---|---|---|---|
| `Pirate` (Blackstar) | 9999 | ✅ yes | ✅ yes (`requiredCount` 1) |
| `PirateWaster` | **9999** | 🔴 **yes** | ✅ no (`requiredCount` 0) |

⇒ **Blackstar is in the default list ✅. "Waster pirate band does not appear at all" ❌** —
it is not in the default list, but it *is* an addable row on the screen. Which half the
criteria meant is ambiguous and is not mine to resolve.

## ⭐ Gate item 1 has LANDED — `SLATE_KEEPS_CONFIGURABLE_1`

`PRE_WORLDGEN_GATE.md` §2 item 1 says `OnlyOurFactions.xml` zeroes
`maxConfigurableAtWorldCreation` and deletes four ratified rows, and calls the checklist
"a trap until this lands". **Measured: the patch no longer touches that field.** Its header
now reads *"🔴 IT NO LONGER TOUCHES maxConfigurableAtWorldCreation, and must not again"*,
and it zeroes `startingCountAtWorldCreation` on 48 defs instead — a cap, not a deletion.

Across every visible FactionDef, exactly **one** reads 0: `OuterRim_RebelAlliance`.
⇒ **The described defect is fixed.** The gate row is stale.

## 🔴 But a different and larger one is real: SEVEN of our factions are not configurable

The engine wants `> 0`. Measured on the live game:

| our faction | `maxConfigurableAtWorldCreation` | on the screen? |
|---|---|---|
| `Jawa_Junkers` | **9999** | ✅ |
| `Jawa_AscendantHelix` · `Jawa_DeepwaterCompact` · `Jawa_FreeDroidEnclaves` · `Jawa_GeonosianFoundryHive` · `Jawa_HuttCartel` · `Jawa_IndigenousTribes` · `Jawa_WildsteamClan` | **−1** | 🔴 **no** |

**Cause, and it is an omission rather than a patch:** `grep maxConfigurableAtWorldCreation
src/Jawa/Jawa_Patches/Defs/FactionDefs/` returns **nothing** — we never set it. Vanilla sets
9999 on the *concrete* defs (`OutlanderCivil`, `TribeCivil`, `Pirate`), not on the abstract
bases. Six of ours inherit `OutlanderFactionBase` and one `TribeBase`, which do not carry
it, so they default to −1.

⭐ `Jawa_Junkers` is configurable **only by accident**: its parent `PirateBandBase` *is* the
`Pirate` def, which carries 9999 — the same inheritance leak that gave it Blackstar's
`forcedMemes`.

## 🔴 And this corrects evidence I recorded yesterday

`seven-authored-factions-…-5b90c7`/run-1 recorded all seven generating with settlements on a
quicktest. **That does not transfer to the owner's world**, and `OnlyOurFactions.xml`'s
header says why:

> *"`requiredCountAtGameStart` is not a safety net. `FactionGenerator.InitializeFactions`
> reads it ONLY where no faction list was configured; worldgen through the screen passes
> `Current.CreatingWorld.info.factions` and adds that list verbatim."*

A dev quicktest takes the **no-list** path, so `requiredCountAtGameStart: 1` carries the
seven in. **A world generated through the Configure Factions screen takes the list path** —
and they are not on the screen, so they cannot be in the list.

⇒ **If the owner builds his world the way he intends, seven of the twelve authored factions
may simply not exist.** That is unretrofittable, and it is the single most expensive thing
found in this run. Filed as `AUTHORED_FACTIONS_OFF_THE_SCREEN_1`.

⚠️ **One thing NOT measured and it decides the severity:** whether `Page_CreateWorldParams`
seeds its default list from `ConfigurableFactions` alone, or unions it with
`requiredCountAtGameStart > 0` defs. If the latter, the seven arrive anyway and this is
cosmetic. **A human looking at the Configure Factions page settles it in ten seconds**, and
that look is now worth more than anything else on this board.
