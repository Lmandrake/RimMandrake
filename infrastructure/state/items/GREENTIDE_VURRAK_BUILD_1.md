# GREENTIDE_VURRAK_BUILD_1 — the false bank

Child of `GREENTIDE_TERROR_REPLACEMENT_1`. Design: `design/Jawa/worldbuilding/biomes/greentide_terror_replacement_design_2026-10-02.md`.

## spec

Owner rulings 2026-10-03 (decision taken by question card; BENCH ledger note on the parent): body = the
weighted crown (only something its size or bigger sets it off; small animals just reveal it); commonness
0.15; it bites anything that steps on it; warning almost none (bite on contact), but the game pauses on the
first-ever reveal.

## built

- `src/RimMandrake/Greentide/Defs/ThingDefs_Races/RM_Vurrak.xml` — `RM_Vurrak` race + kind (body 1.85,
  not a predator), `RM_BankDisguise` invisibility hediff. Placeholder art: the dhollock retinted.
- `src/RimMandrake/Greentide/Source/RM_CompBankAmbusher.cs` — lies flat and invisible on bank cells
  (standable, not deep, water within 2.9); a stepper of body size >= `vurrakTriggerBodySize` (0.6) on its
  cell is bitten at once and then fought; lighter ones reveal it; damage reveals it; eats its kill where it
  fell. `RM_GameComponent_Vurrak` pauses + letters on the first reveal seen by colonists (once per game).
  `RM_VurrakProof.ProofStepOn` for `jawa/static_call`.
- Settings (Greentide): `vurrakAmbushEnabled`, `vurrakTriggerBodySize`, `vurrakFirstRevealPause`; the
  settings window now scrolls.
- Inline in `RM_Greentide` `<wildAnimals>` at 0.15. Validation chain `vurrak` (3 bars).
- Art queued: `infrastructure/artpipe/art_lists/greentide_vurrak_2026-10-03.csv` (3 jobs).

## verify

- [ ] Live: `vurrak` chain GREEN (colonist STRUCK, hare REVEALED, toggle off REFUSED).
- [ ] Live: first reveal in front of colonists pauses and sends "The bank moved" once.
- [ ] Art landed and wired in place of the retinted dhollock.
