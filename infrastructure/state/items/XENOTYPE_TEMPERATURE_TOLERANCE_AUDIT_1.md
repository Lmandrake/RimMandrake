## spec
🔴 **Ash'karr is a desert world and nobody has ever checked which of the 128 reachable
xenotypes can survive it.** Owner, 2026-08-22, on the back of the cold-nursery ruling:
*"Please add a BUILD queue item to evaluate the temperature tolerances of the xenotypes
available."*

**The world, measured** against `world/ASHKARR_WORLDMAP_tiles.csv` (21,872 tiles):

    annual mean temperature   min -82.0 C   median 12.9 C   max 66.1 C
    tiles above 32 C on the ANNUAL MEAN   6,276  (29%)

⚠️ **An annual mean is not a summer afternoon.** RimWorld swings a map's temperature by
season and by time of day around that mean, so the lived maximum on a hot tile is well
above 66 C and the lived minimum on a cold one well below -82 C. Any tolerance judged
against the mean alone is judged against the mildest number the world offers.

## the question, in three parts
1. **Which xenotypes carry a comfort-band gene at all?** The vanilla family is
   `MinTemp_*` / `MaxTemp_*`, which offset `ComfyTemperatureMin` and `ComfyTemperatureMax`.
   Report every reachable xenotype's NET offset, not the gene names — a species with
   `MinTemp_SmallIncrease` and `MaxTemp_LargeIncrease` (which is what `MandrakeJawa` has)
   has a shifted band, not a wider one, and the two are not the same thing.
2. **Which of them can actually live where their faction lives?** Cross the band against
   the tiles that faction holds, not against the planet average. A Wildsteam clan in the
   cold belt and a Trade Moot on the terminator face different problems.
3. **Which species are in the wrong place?** A species whose lore says desert and whose
   genes say temperate is a defect worth naming; so is the reverse.

## why it is worth doing now and not at playtest
🔑 **Heatstroke and hypothermia are silent until they are lethal.** A pawn outside its
comfy band takes a rising hediff with no red error and no log line, exactly like the
bare-handed and empty-tag-pool failures this project has already paid for twice. The
instrument exists — the def dump carries every gene's `statOffsets` — so this is an
offline census, not a playtest.

⚠️ **This is also the other half of the cold-nursery ruling** (`jawa_society.md` §4.3a).
The egg's hard ceiling is 32 C. If the Jawa's own `MaxTemp_LargeIncrease` lets the ADULTS
work comfortably at 40 C, then the clan is comfortable in exactly the places its clutch
cooks — which is a wonderful tension and should be a *known* one.

## verify
- a table of every REACHABLE xenotype with its net `ComfyTemperatureMin` /
  `ComfyTemperatureMax` offset, sourced from the live dump, with the genes that produce it
- the count of xenotypes with NO temperature gene at all, stated as a measured number
- for each of the twelve authored factions, whether its xenotypes' bands cover the tiles
  it actually holds
- ⛔ no number in the report may come from `grep` over the dump; `measure` or a python
  json read, per `CLAUDE.md`

## criteria
A named list of xenotypes that cannot survive where their faction is placed, or a measured
statement that none exists. Either answer closes it; a report that does not say which
species are in trouble does not.

## watch out
⚠️ **`ComfyTemperature` is not survival.** Comfy band is where a pawn is content; the
lethal band is wider and is governed by hediffs, apparel insulation and indoor
temperature. A species outside its comfy band on its own tiles is a mood and productivity
problem; one outside the survivable band is a death sentence. Report both and do not
conflate them.
⚠️ **Apparel is a confound and belongs in the answer.** A Jawa in a robe and hood is not a
naked Jawa, and `faction_equipment_clusters.md` already records what each faction wears.
⚠️ The tiles CSV carries `temp_c` as the annual mean and nothing else. If a per-season
figure is needed, it comes from the bridge on a live world, which makes that half a CHECK
question rather than a BUILD one — say so rather than estimating it.
