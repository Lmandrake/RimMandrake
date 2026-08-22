# Two items settled off one window — CHECK, 2026-08-21 ~17:30 PDT, 578 mods


> 🔴 **SUPERSEDED IN PART, 2026-08-22 — do not read the faction roster here as settled.**
> `infrastructure/state/observed/2026-08-22/configure_factions/README.md` (`AUTHORED_FACTIONS_OFF_THE_SCREEN_1`)
> finds that *"seven of the twelve authored factions may simply not exist"* in the owner's
> world. This file's *"all seven generated, all seven hold settlements"* was measured on a
> DIFFERENT world — and the owner is now remaking the planet (`canon.yml planet.status: remaking`).
> ⛔ Nobody reads backwards, so this pointer lives here rather than only in the newer file.

## `IKEE_READS_AS_OURS_1` — PASS, second run, and it nearly produced a false alarm

| check | reading |
|---|---|
| `ThingDef/AA_Eyeling` label | **`ikee`** |
| `PawnKindDef/AA_Eyeling` label | **`ikee`** |
| description contains "extradimensional corruption" or "grotesquely" | **no** |
| biomes where it can spawn | **exactly 3** — `ExtremeDesert` 0.5, `Wasteland` 1.2, `ZBiome_DesertOasis` 0.8 |

Matches the criteria exactly, including "NOT ON THE NIGHTSIDE" — nothing polar or cold in
the list.

### 🔴 The trap, recorded so nobody repeats it
A first pass asked "which biomes list `AA_Eyeling` in `wildAnimals`" and got **79**,
including `Ocean`, `Space`, `Orbit`, `IceSheet` and `MetalHell`. That number is garbage.

**`BiomeDef.wildAnimals` lists EVERY animal in the game, not the ones that live there** —
`Ocean` carries **1024** `BiomeAnimalRecord` entries — and the ones that cannot spawn are
present with **`commonality: 0`**. ⇒ Membership in `wildAnimals` means nothing. **Filter on
`commonality > 0`** or you will report a desert animal as living in orbit.

## `seven-authored-factions-generate-and-field-their-own-kinds-5b90c7` — parts 1 and 2 PASS

All seven generated, all seven hold settlements on the world (`jawa/list_factions`):

    Jawa_HuttCartel 6    Jawa_Junkers 4    Jawa_AscendantHelix 3    Jawa_DeepwaterCompact 2
    Jawa_FreeDroidEnclaves 2   Jawa_GeonosianFoundryHive 1   Jawa_WildsteamClan 1

And the other five authored factions are present too: `Jawa_IndigenousTribes` 3,
`OutlanderCivil` 3, `TribeCivil` 2, `Empire` 1, `Pirate` 1. **105 settlements on the planet
across 37 visible factions.**

⚠️ **Part 3 is UNMEASURED and it is the half that matters** — "its raids arrive as ITS OWN
pawn kinds, not vanilla ones". No raid was provoked in this window. The item's own warning
applies: a faction with settlements looks like it works until you read the arriving pawns'
kindDefs. That is why the run is `partial`, not `pass`.
