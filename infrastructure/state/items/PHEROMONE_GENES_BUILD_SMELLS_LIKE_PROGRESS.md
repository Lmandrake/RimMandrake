## why
Follow-up of `SPECIES_TRAITS_OVER_APTITUDES_1` (owner 2026-09-20: a species gene REPLACES the
aptitude that was its surrogate). Zeltron and Falleen still carry `AptitudeStrong_Social` as the
stand-in for their pheromones (canon: `design/RimStarWars/canon_references/zeltron/description.md`,
"capable of producing powerful pheromones"; check the falleen entry before building).

Pheromones act on OTHER pawns, so the StatWorker-only shape of `RSW_SpeciesCharacter.xml`
(`src/RimStarWars/StarWarsRaces/Defs/GeneDefs/`) does not fit as is: likely a gene-gated
opinion ThoughtWorker on pawns near the carrier (the Ikee thought,
`src/RimStarWars/SWBestiary/Source/JawaIkee/`, is the template), with its own Mod Setting.

## verify
Zeltron and Falleen carry a pheromone gene a player can see working (an opinion line on pawns
near them), `AptitudeStrong_Social` is gone from both through `gen_races_mod.py`
OWNER_GENE_REMOVALS, and `selftest_species_character_genes.py` covers it.
