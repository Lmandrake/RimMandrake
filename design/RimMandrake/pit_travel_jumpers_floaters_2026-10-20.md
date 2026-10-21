# Pit travel: which creatures jump or float (tagged from lore, 2026-10-20)

Owner, by card 2026-10-20, typed: *"2 now, (1) later during the animal normalization pass (blocked by biomes being
complete)"*. This is the "2 now" half: races tagged FROM LORE so that bar `jump_into_pit_lands_unhurt` has creatures to act
on. The owner's review of this list is owed in the animal-normalization pass (item `PIT_TRAVEL_TAGS_REVIEW_LORE_FIRST_GUESS`).

Mechanism: `RM_PitTravelExtension` (`jumps` / `floats`) patched onto each race by
`src/RimMandrake/FlowWorks/Patches/Canals/FlowWorks_PitTravel.xml`. Read by `RM_PocketGrid.FreePitTraveller`, gated by Mod
Setting `pitFreeTravelEnabled`. A tagged creature crosses pit walls freely, is never held in a pit, and takes no fall on
arriving. Flyers (`MaxFlightTime` > 0) are free already and carry no tag.

Method: every race ThingDef under `src/RimMandrake`, `src/RimStarWars`, `src/RimUtinni` whose description matches
leap/bound/hop/hover/drift/float/levitate/jump/bounce/balloon/aloft/spring, flyers excluded, each read by hand. RSW canon
entries in `design/RimStarWars/canon_references/` were checked where they exist (tooke, frogdog).

## Floaters (`floats`)

| race | evidence |
|---|---|
| `RM_Bulloo` | "A small, floating, gas-filled creature that drifts on the hydrogen ... bouncing gently off whatever stands in its way" |
| `RM_ColossalAerofleet` | "A bulloo grown to enormous size ... everywhere it drifts" (a giant bulloo) |
| `RM_InfectedAerofleet` | "A bulloo is nothing but a floating ball of gas: no feet ... drifted into the Contagion on the wind" |
| `RM_OcularJelly` | "A drifting, gas-filled shape that hangs at canopy height" |
| `RM_Gawpsack` | "A drifting translucent bag ... reads the cloud from canopy height and sinks, all at once" |
| `RM_Drifter` | "A head-sized bladder ... drifting a hand's breadth above the floor ... It floats on methane" |
| `RM_Garsulix` | "A floating, chitinous, insect-like ball of gas ... It drifts ever closer" |

## Jumpers (`jumps`)

| race | evidence |
|---|---|
| `RM_Huldu` | "crosses open stone in startling bounding hops off the fluke" |
| `RM_Sipper` | "Sippers hop toward the brightest light near them" (thumbnail-sized swarm vermin) |
| `RSW_Tooke` | canon entry: "small, hopping rodents"; "run quickly and jump long distances" |
| `RSW_FrogDog` | canon entry: "The creatures hopped and waddled from place to place" |
| `RSW_SandLeaper` | "it bounds on two long, many-jointed hind legs" (no canon entry in the library to check) |
| `RSW_CaveLemming` | "becomes a sudden, springing leap the instant danger closes" (no canon entry in the library to check) |

## Matched a word but left out (for the review)

- Water drifters (they float in a sea or fuel, not in air): `RM_Lunoowa`, `RM_Maalu`, `RM_Fessu`, `RM_Oovu`, `RM_Bladderboil`,
  `RM_Suulk`, `RM_ReefbackJuv`, `RM_DancingSkresh` ("aloft in the dim water"), `RSW_Faa`, `RSW_FaaJuv` ("drift-shrimp").
- Ground crowds, where "drift" means slow movement: `RM_Gappo`, `RM_Fubbum`, `RM_Saluksis` ("drift across the jungle floor"
  on thin legs), `RM_Titanoslime` (shapes drift inside it).
- Other senses of the word: `RM_Murrek` and `RM_Dhokkur` (snow or ash drifts), `RM_Guzzka` ("a drift of bleached ... stone"),
  `RM_Kethrel` ("bound with tar"), `RM_Surrik` ("root-bound"), `RM_Siidda` (carried aloft by sandstorms, dormant).
- Borderline: `RM_Tebbra` ("within a few bounds of the nearest shade" measures distance, not gait). Not tagged.
- Walkers whose later text says "drift(ing)": `RM_Rakeshank` (four long legs), `RM_Durrok` (a quadruped), and `RM_Corrik`
  (a bladder riding the shore current, so a water drifter). Not tagged.
- Leapers already on `RM_ClimbAbility.leaper` (vanilla hare, snowhare, cat, lynx) climb one level more and are NOT free
  travellers.
