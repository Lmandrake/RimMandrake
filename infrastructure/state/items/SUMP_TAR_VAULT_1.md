# SUMP_TAR_VAULT_1 — the tar larder, and extraction as the solvent's economy

Owner ruling 2026-09-24, typed on the question card (his free-text answer),
verbatim:

> "I love this, but it requires solvents to extract things or else they are
> rendered useless. So extraction is a solvent based economic need. Interesting.
> Never seen that mechanic before."

## spec

- **The vault**: a buildable tar-pit store (pit or sunk barrel-rack). Anything
  sealed in it is perfectly preserved — food, corpses, hides never rot. Sealing
  is cheap; the tar does the work. (Fiction: the trap that remembers, working for
  you — and the slow-growing dorvel makes a deep pantry matter.)
- **The catch — extraction is solvent-gated**: retrieving an item without solvent
  yields it tarred/ruined (useless). Cleaning it out costs solvent per item —
  the same acid as `SUMP_GASLIGHT_1`'s reaction (one acid, three uses). Weak
  local acid (seepwax) covers routine use, ruled generous — not a starvation
  mechanism; strong foreign acid trivializes it (trade reward,
  `BIOME_NUISANCE_NORMALIZATION_1`).
- **Implementation**: rot-stop is a container comp (vanilla-adjacent); the gate is
  an extraction bill/job consuming solvent, else the tarred variant comes out.
- **Ship candidate** (`BIOME_SHIP_CONTRIBUTIONS_1`): a vault larder module
  buildable aboard — candidate row, not yet owner-confirmed for the ship list.
- Mod Settings toggle per the standing law; tuning per `SUMP_TAR_NASTINESS_1`'s
  dirty-colony law.

## verify

Quicktest: sealed food never rots; extraction without solvent yields a ruined
item; with solvent, the clean original; solvent consumption scales per item.

## criteria

The planet's best pantry is in its nastiest biome, and the price of the archive
is paid in acid.
