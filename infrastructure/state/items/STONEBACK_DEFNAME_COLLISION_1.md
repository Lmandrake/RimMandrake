# STONEBACK_DEFNAME_COLLISION_1 — one defName, two different animals

## what is wrong — MEASURED 2026-09-21

`RSW_Stoneback` is declared **twice**, as both a `ThingDef` and a `PawnKindDef`, in two
directories the game **does** load:

| file | label | bodySize |
|---|---|---|
| `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml` | **bokka** | **0.4** |
| `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml` | **korrum** | **4.00** |

These are not a duplicate of one creature — they are **two different creatures**, a small
one and a giant one, colliding on a single defName. RimWorld keeps one and discards the
other, so one of these animals does not exist in the shipped game and nothing says which.

🔑 **The collision has already produced two contradictory facts in our own files**, which is
how it was found. The two biomes that wire it each describe a *different* animal:

- `RUT_Desert.xml:259` — `0.5`, comment *"bokka - anywhere on the dayside, import"*
- `RUT_ExtremeDesert.xml:143` — `0.025`, comment *"bouldermit - giant, keep"*

The second names a third creature entirely (`AA_BoulderMit`) and calls it giant, which fits
`korrum` (4.00), not `bokka` (0.4). ⚠️ So that row may ALSO be a mis-wiring — someone may
have meant `AA_BoulderMit` and typed the stoneback. Check before deleting it, or the
Stillsand silently loses a giant it intended.

## why it blocks a ruling

The owner ruled 2026-09-21 that **an animal belongs to one biome** (`BIOME_SPECIFIC_FAUNA_LAW_1`)
and, asked where the stoneback should live, ruled *"Neither — give it to a thinner roster"*.
That ruling **cannot be executed as stated**, because "the stoneback" is two animals. BENCH
was about to give it to the Scarlands on the evidence that it is bodySize 0.4 and therefore
improves that roster's weak food pyramid (53.0% small, the thinnest of the candidates at 8
wired species) — a rationale that is **only valid if `bokka` is the survivor**. If `korrum`
(4.00) wins the collision, the same move puts a giant into the weakest pyramid on the planet.

⛔ Do not wire, unwire or evict any stoneback row until the identity is settled.

## needs him — one question

**Which creature keeps `RSW_Stoneback`, and what is the other one called?** Both are already
authored; this is a naming call, not new content. The likely shape: the BiomesTeam port keeps
a `BMT`-derived name and the DesertPort creature takes `RSW_Korrum` (or vice versa), after
which `BIOME_SPECIFIC_FAUNA_LAW_1` applies to **each** separately — two creatures, two homes.

## spec

1. Get the naming ruling above.
2. Rename the loser's `ThingDef` **and** its `PawnKindDef`, plus every reference: the two
   biome wirings, the five roster rows that name a stoneback (`desert.json` — renamed to
   `RSW_Stoneback` at `b173e699d` and now ambiguous, `arid_shrubland.json`,
   `the_scarlands.json`, `wasteland.json`, and whatever `dune_sea_deep_desert.json` intends
   given `RUT_ExtremeDesert` wires it with no roster row at all), and any texPath/art
   registry entry keyed on the defName.
3. Resolve `RUT_ExtremeDesert.xml:143` on its own evidence — is that row the giant it says
   it is (`AA_BoulderMit`), or a mis-typed stoneback?
4. Then, and only then, apply the one-home ruling to each creature.

## verify

`RSW_Stoneback` resolves to exactly one `ThingDef` and one `PawnKindDef`; the other creature
has its own defName; no roster row or biome wiring is ambiguous about which animal it means;
a load log shows no duplicate-defName error for either. ⚠️ The load-log half needs the
Desktop — it cannot be checked from the Mac.

## criteria

Every animal we ship has a name that means exactly one animal.

## Noted from the same measurement, and NOT a defect

The same scan reported **32** same-type/same-defName collisions. **30 of them are inert**: a
byte-identical copy of the vault def tree sits under
`src/RimUtinni/StructureInjectionsRUT/Source/Defs/`, duplicating
`.../Defs/VaultDungeons/`. The mod has no `LoadFolders.xml`, so RimWorld loads the root
`Defs/` only and never that `Source/` path — the copies are dead files, not live collisions
(⚠️ convention-based; the authoritative check is a load log on the Desktop). They are still
worth deleting, because they make every future defName measurement over-report by 30 — this
one did, before the def **type** was taken into account. Only `RSW_Stoneback` (its ThingDef
and its PawnKindDef) is real.
