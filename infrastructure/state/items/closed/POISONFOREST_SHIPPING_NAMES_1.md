# POISONFOREST_SHIPPING_NAMES_1 — Owner card: poison_forest working names (vent stalker, dark crust)

## the ask

`COMMISSION_LEDGER_CLEANUP_1`'s poison_forest sheet slice shipped two new
defs under working names, both flagged "working name only" in their own file
headers:

- **`RSW_VentStalker`**, label "vent stalker" — the eyeless ground-sense
  ambush predator, body/art reskinned from the already-ported `RSW_Kinrath`.
  `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_VentStalker.xml`.
- **`RUT_DarkCrust`**, label "dark crust" — the black/purple/red phototroph
  film groundcover (art job `rutdarkcrust_v1` queued, not yet landed).
  `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Plants/RUT_PollutedFlora.xml`.

`poison_forest.md` itself names no naming gap in an "Owed" section the way
`arid_shrubland.md` does (checked — no such list exists in that doc), so
unlike `ARIDSHRUBLAND_SHIPPING_NAMES_1` this card is not consolidating a
pre-existing owed-names list, only the two working names this pass minted.

## the decision this needs

For each, pick one — or write your own, which beats every option here:

1. **The vent stalker** (`RSW_VentStalker`) — blind, presses flat against a
   trunk, reads the vents' constant chemical hum through its feet.
   Alternatives in the register of Kinrath's own donor flavor ("blind,
   heat/vibration-sensing ambusher"): "hush-walker", "ground-listener",
   or something closer to the Jawa naming register used elsewhere in this
   biome's roster (Mynock, Neebray — plain Star Wars nouns stay as-is; this
   is an invented creature, so per `Q11a` it may freely take a plain
   descriptive or invented name, no canon-IP constraint applies).
2. **The dark crust** (`RUT_DarkCrust`) — the biome's marginal phototroph
   film, "the ecological equivalent of moss on a north wall"
   (poison_forest.md §4). "Dark crust" is plain and descriptive;
   alternatives could lean into the biome's own register (something
   evoking "starward film" or "the losers' moss", per its own text) or stay
   plain-English.

## why it matters

Neither name gates anything mechanically — both defs are fully functional
under their working names — but a defName's `<label>` is player-facing text,
and both creature/plant will show up in-game (bestiary tab, butcher menu,
harvest list) under whatever ships here. Better decided once, deliberately,
than drifted into by whichever name happened to get typed first.

## verify

Owner picks (or supplies) a label for each of the two; whoever applies the
ruling updates the `<label>` field only (never the `defName` — a rename this
late would need its own cross-reference sweep, out of scope for a naming
card) and notes the ruling here.
