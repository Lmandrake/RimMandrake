# Raid-spawn split, measured live 2026-08-30 (FOUNDRY)

Evidence for `SIX_FACTIONS_NEVER_RAID_1`. Live 590-entry mod list, `Map_0` of a scratch
quicktest colony (3 colonists), game PAUSED throughout, `ticksGame` 1176→4236.
Every raid was fired with `jawa/fire_raid {points, faction, dryRun:false,
strategy:"ImmediateAttack", arrivalMode:"EdgeWalkIn"}`; arrivals counted off
`map.mapPawns.AllPawnsSpawned` before/after, and the map cleared with
`jawa/destroy_bulk nonColonists` between firings.

## The split — 8 consecutive firings each, 3000 points

    Empire                    [27,30,32,29,29,35,34,30]   8/8
    Insect                    [42,29,34,44,42,34,32,34]   8/8
    OutlanderCivil            [27,27,27,30,27,27,26,47]   8/8
    TribeCivil                69 · 78 (2 firings)         ✅
    TradersGuild              [19,0,20,19,0,0,20,0]       4/8
    Pirate            VANILLA [0,0,0,0,0,0,0,0]           0/8
    CASacrilegHunters   a mod [0,0,0,0,0,0,0,0]           0/8
    Jawa_HuttCartel           [0,0,0,0,0,0,0,0]           0/8
    Jawa_Junkers              [0,0,0,0,0,0,0,0]           0/8
    Jawa_AscendantHelix       [0,0,0,0,0,0,0,0]           0/8
    Jawa_FreeDroidEnclaves    [0,0,0,0,0,0,0,0]           0/8
    Jawa_IndigenousTribes · Jawa_WildsteamClan · Jawa_GeonosianFoundryHive ·
    Jawa_DeepwaterCompact                                 0 in every firing

## Points sweep — 70 · 150 · 400 · 1000 · 3000 · 10000 · 30000

    Jawa_HuttCartel        0 at every value
    Jawa_IndigenousTribes  0 at every value
    OutlanderCivil         pawns at every value

## Files

| file | what |
|---|---|
| `run11.py` | the 8×-per-faction firing loop that produced the split table |
| `run12.py` | the points sweep |
| `kinds.py` | live read of all 49 roster `PawnKindDef`s — all found, all `isFighter` |
| `split.py` | diffs all public `FactionDef` fields, failing group vs working group |
| `defs3.json` | named `FactionDef` fields for 7 factions |
| `defs4.json` | ALL 122 public fields for 7 factions — `split.py`'s input |

`split.py` output: **no field separates the two groups, in either direction.**

## The harness defect that voids the 2026-08-27 evidence

`jawa/set_faction_relation kind=Hostile` is a no-op for any goodwill-bearing pair —
`Faction.SetRelationDirect` (`RimWorld/Faction.cs:641`) logs an error and returns when
`HasGoodwill && other.HasGoodwill`. `jawa/faction_relations_set` is the tool that works.
Full write-up in `.claude/skills/rimbridge/references/traps.md`.
