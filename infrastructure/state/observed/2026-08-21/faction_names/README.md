# FACTION_NAMES_ARE_GENERATED_1 — the premise has expired, and the instrument over-reports

**CHECK, 2026-08-21 ~17:20 PDT. 578 mods, dev-quicktest world.** No repair was run: this is a
scratch world, and `faction_name_set` on it would prove nothing about the real one.

## 🔴 All twelve authored factions carry a `fixedName`, and all twelve wear it

| defName | live name | `defFixedName` |
|---|---|---|
| `Empire` | Galactic Empire | Galactic Empire |
| `OutlanderCivil` | Homestead Defense League | Homestead Defense League |
| `TribeCivil` | Deep Desert Tribes | Deep Desert Tribes |
| `Pirate` | Blackstar Company | Blackstar Company |
| `Jawa_AscendantHelix` | Ascendant Helix | Ascendant Helix |
| `Jawa_DeepwaterCompact` | Deepwater Compact | Deepwater Compact |
| `Jawa_FreeDroidEnclaves` | Free Droid Enclaves | Free Droid Enclaves |
| `Jawa_GeonosianFoundryHive` | Geonosian Foundry Hive | Geonosian Foundry Hive |
| `Jawa_HuttCartel` | Hutt Cartel | Hutt Cartel |
| `Jawa_Junkers` | the Junkers | the Junkers |
| `Jawa_IndigenousTribes` | Jawa Trade Moot | Jawa Trade Moot |
| `Jawa_WildsteamClan` | Wildsteam Clan | Wildsteam Clan |

**12 of 12.** ⇒ The item's spec — *"Ten factions are wearing names the dice picked"*, naming
`Jawa_HuttCartel`, `Jawa_IndigenousTribes`, `Jawa_AscendantHelix`, `Jawa_DeepwaterCompact`,
`Jawa_FreeDroidEnclaves`, `Jawa_GeonosianFoundryHive`, `Jawa_WildsteamClan`, `Jawa_Junkers`,
`OutlanderCivil`, `TribeCivil` — **is no longer true of any of them.**

🔑 **This also retires a pre-worldgen gate row.** `PRE_WORLDGEN_GATE.md` §2 item 4 says
*"Eleven of the twelve NAMED factions have no `fixedName` (only `Empire` carries one)"*.
Measured live, that is stale: all twelve carry one. `FACTION_FIXEDNAME_ELEVEN_1` has landed.

## ⚠️ The criteria as written cannot be met, by anything

It asks for *"every `currentName` equals its `defLabel`"*. A faction with a `fixedName` that
differs from its label — which is the whole point of a reskin — can **never** satisfy that.
`Empire`'s label is "The Galactic Empire" and its fixedName is "Galactic Empire"; they are
supposed to differ. The successor criteria should compare `currentName` to **`defFixedName`**,
falling back to `defLabel` only where no fixedName exists.

## 🔴 `jawa/faction_name_get` reports 24 generated. Nine of them are not.

    tool: "24 faction(s) are wearing a GENERATED name."

Split by hand against `defFixedName`:

| | count |
|---|---|
| wearing their own `defFixedName` — **false positive** | **9** |
| no `defFixedName` at all — genuinely generated | **15** |

The nine false positives are `Empire`, `Jawa_Junkers`, `PirateYttakin`, `DV_PirateKeshig`,
`AG_XenohumanPirates`, `CannibalPirate`, `BS_Muspelheim`, `BS_Niflheim`, `BS_OgreFaction` —
i.e. the flag fires on exactly the factions that are **correct**. `isGenerated` is really
"`currentName != defLabel`", which is a different question. ⛔ Do not drive a repair off
`generatedCount`; it would clear names that were deliberately set.

## What is genuinely still random — and none of it is ours

Fifteen third-party mod factions, on a world that will be frozen and shipped:

    TribeRoughNeanderthal -> Luddus            TribeSavageImpid -> League of Necuvizz
    OutlanderRoughPig -> Gemoinund Accord      DV_OutlanderRoughBuzzer -> Cloud of Thschit
    Horrors -> The Dark Swarm                  KAR_OrcClan -> The Trosma People
    VRESaurids_... -> Pob'Rokba Coalition      AG_OutlanderCivilUnion -> Eraistia
    VFEP_Junkers -> The Anti-Love Imps         VFEP_Mercenaries -> The Raiders
    OuterRim_BinaryStarRaiders -> The Pistol Bears
    OuterRim_MoistureFarmers -> Pact of Vearelia
    BS_LittlePeople -> Gaboofweg               BS_Dvergr_Medieval_Union -> Western Oulora
    TradersGuild -> Cosmic Nexus

Whether "The Anti-Love Imps" and "Cosmic Nexus" are acceptable on the shipped planet is a
scope call, not a defect.

## Not done
⚠️ The item's deciding visual check — click a Junkers settlement on the world map and read
the faction name on screen — **was not performed.** That is why this run is `partial`.
