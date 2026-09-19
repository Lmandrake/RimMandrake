# SAND_SWIMMERS_MOD_1 — sand fishing in deep-sand pools; the sand swimmers mod

Owner, 2026-09-06, verbatim in intent: *"maybe even a new concept of Sand Fishing in
certain pools of Deep Sand you can't even walk over, that's really cool! Let's do that! But
the sand fish don't look like fish of course, just analogs. Part of the 'sand swimmers'
mod we are going to make."*

## spec
- **Deep Sand** terrain: pools of sand you cannot walk over (impassable like deep water,
  but sand) — placed in the dune sea / deep desert / Cracked Lands flats per their sheets.
- **Sand fishing**: fishable like water (Odyssey's fishing spot / job on the new terrain —
  read the fishing system's terrain requirements before designing; likely a terrain
  affordance + `fishTypes` on the biome, or a Harmony extension if fishing is hard-bound
  to water).
- **The sand fish**: analogs, never fish-shaped — sand swimmers (the sand prowler's
  burrow-swim is the existing precedent; the Blue Desert's sand-swimmer gene cites it);
  a small family: the catch, the thing that catches the catcher, the rare prize.
- The mod: `RUT_`/`RSW_` per the naming grammar (Star Wars sand-swimmers → `RSW_`); art to
  the NEW-ART ledger; anti-exponential check on food yield (a desert that feeds you from
  sand must stay a thin windfall, not a farm).
- Ties: `FISH_BY_BIOME_1`, `dune_sea.md`, `deep_desert.md`, `the_cracked_lands.md`.

## verify
A quicktest map with a deep-sand pool: pawns cannot path across it, a fisher catches a
sand swimmer from it, the catch is an analog (art reviewed by the owner).
