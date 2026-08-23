## spec
🔴 **Seven of the eight authored `Jawa_*` factions are not on the Configure Factions
screen**, because `maxConfigurableAtWorldCreation` was never set on them.

`FactionGenerator.ConfigurableFactions`, quoted from `OnlyOurFactions.xml`'s header:

    from f in DefDatabase<FactionDef>.AllDefs where f.maxConfigurableAtWorldCreation > 0

Measured live, 2026-08-22:

| faction | value | configurable |
|---|---|---|
| `Jawa_Junkers` | **9999** | ✅ |
| `Jawa_AscendantHelix` | −1 | 🔴 |
| `Jawa_DeepwaterCompact` | −1 | 🔴 |
| `Jawa_FreeDroidEnclaves` | −1 | 🔴 |
| `Jawa_GeonosianFoundryHive` | −1 | 🔴 |
| `Jawa_HuttCartel` | −1 | 🔴 |
| `Jawa_IndigenousTribes` | −1 | 🔴 |
| `Jawa_WildsteamClan` | −1 | 🔴 |

**Cause.** `grep maxConfigurableAtWorldCreation src/Jawa/Jawa_Patches/Defs/FactionDefs/`
returns nothing — we never write it. Vanilla sets `9999` on the **concrete** defs
(`OutlanderCivil`, `TribeCivil`, `Pirate`), not on the abstract bases; six of ours inherit
`OutlanderFactionBase` and one `TribeBase`, neither of which carries it, so all seven
default to −1.

⭐ `Jawa_Junkers` is configurable **by accident** — `PirateBandBase` *is* the `Pirate` def,
which carries 9999. The same inheritance leak that gave the Junkers Blackstar's
`forcedMemes` also gave them a screen row.

## 🔴 why this may be the most expensive open item
`OnlyOurFactions.xml`'s header, on the two worldgen paths:

> *"`requiredCountAtGameStart` is not a safety net. `FactionGenerator.InitializeFactions`
> reads it ONLY where no faction list was configured; worldgen through the screen passes
> `Current.CreatingWorld.info.factions` and adds that list verbatim."*

- **Dev quicktest** — no list configured ⇒ `requiredCountAtGameStart: 1` carries all seven
  in. This is why they generated with settlements when CHECK measured them, and why that
  measurement does **not** transfer.
- **A world built through the screen** — the configured list is used verbatim, and they are
  not on the screen to be in it.

⇒ **If the owner builds his one hand-made world the way he intends, seven of the twelve
authored factions may not exist in it.** The world is frozen and shipped, so there is no
regenerate behind it.

## ⚠️ the one thing that decides the severity, and it is a ten-second look
Whether `Page_CreateWorldParams` seeds its default selection from `ConfigurableFactions`
alone, or unions it with `requiredCountAtGameStart > 0`. If the latter, the seven arrive
anyway and this is cosmetic — a missing row the owner cannot tick, on factions he was not
going to untick.

🔑 **A human opening the Configure Factions page settles it.** CHECK could not: the main
menu draws its buttons in an `ImmediateWindow` that `get_ui_layout` does not decompose, and
`get_screen_targets` is empty there. **Do that look before building anything.**

## the fix if it is real
Add `<maxConfigurableAtWorldCreation>9999</maxConfigurableAtWorldCreation>` and a sensible
`configurationListOrderPriority` to the seven FactionDefs. They are hand-authored files
under `src/Jawa/Jawa_Patches/Defs/FactionDefs/`, not generated, so this is a direct edit.
⚠️ Set it on **our own defs**, not on the abstract bases — patching `OutlanderFactionBase`
would hand a screen row to every outlander faction in 578 mods.

## criteria
`jawa/get_defs` reports `maxConfigurableAtWorldCreation > 0` on all eight `Jawa_*`
factions, and the owner confirms all eight appear on the Configure Factions page.

Evidence: `observed/2026-08-22/configure_factions/`.
Retires: `PRE_WORLDGEN_GATE.md` §2 item 1 as written — see that file's correction.
