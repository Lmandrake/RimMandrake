# DRAGONSNAKE_PAIR_BUILD_ONE_PALE_ONE_PROPER

## What
Owner, 2026-10-17 (canon blog-image review sheet, dragonsnake note, verbatim): "Split into two official
versions. The two pale versions let's call Dragonsnake_albino. The Jedi Fallen Order four variants lets
accept as the canon Dragonsnake. Comission both in our Star Wars fauna mod."

Build in `src/RimStarWars/SWBestiary` (the Star Wars fauna mod):
1. `RSW_Dragonsnake` (exists: `Defs/ThingDefs_Races/RSW_Dragonsnake.xml`, body in
   `Defs/Bodies/RSW_MlieWaveC_Bodies.xml`) — bring its art to the canon spec: the *Jedi: Fallen Order*
   dark olive-to-slate crocodilian quadruped. Its current donor sprite is tan/khaki (fails the colour item).
2. A NEW Dragonsnake_albino creature (defName per `design/NAMING_SCHEME_PLAN.md`, e.g. `RSW_DragonsnakeAlbino`):
   the pale bone-white limbless serpent of *The Mandalorian and Grogu*.

## Specs (the acceptance bar is each entry's `## Must show`)
- `design/RimStarWars/canon_references/dragonsnake/description.md`
- `design/RimStarWars/canon_references/dragonsnake_albino/description.md`

## Watch out
- Albino is LIMBLESS — a different body plan from RSW_Dragonsnake's quadruped BodyDef; do not reuse it blindly.
- Art goes through the art ledger (`art install`); check existing regenerated art first.
- Ships with its first functional script and Mod Settings toggle, like every new mod content.
