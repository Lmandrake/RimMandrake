# DONOR_FOUR_RETIRE_JUST_GET_IT_DONE

Retire four donor mods: Star Wars Animal Collection (`mlie.starwarsanimalcollection`), Alpha Animals
(`sarg.alphaanimals`), the AA Outposts patch (`daria40k.alphaanimalspatchoutposts`) and Alpha Biomes
(`sarg.alphabiomes`). Owner, 2026-10-18: "Just put in placeholder art for now or donor copies and retire these mods!!!
Just get it done." Offline port and census: `design/RimMandrake/donor_art_census_2026-10-18.md`.

## spec
- No mod of ours hard-depends on the four; our defs that came from them are ported under our prefixes.
- The live mod list and the canonical start save hold none of the four.

## verify
- `donor_retire_census.py refs`: 0 About.xml dependencies on the four in `src/`.
- The `activeMods` of the live ModsConfig and the `modIds` of the canonical start save
  (`infrastructure/state/canon.yml` `planet.start_savegame`) hold none of the four packageIds.

## criteria
- A1..A5 on the ledger (`rimflow show DONOR_FOUR_RETIRE_JUST_GET_IT_DONE`).

## refs
file: src/RimMandrake/Utils/donor_retire_census.py
file: infrastructure/state/CANONICAL_SAVE.md
