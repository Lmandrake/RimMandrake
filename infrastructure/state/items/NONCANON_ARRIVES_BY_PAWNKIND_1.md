# NONCANON_ARRIVES_BY_PAWNKIND_1 — a scope call, not a defect

`XENOTYPE_ROSTER_PURE_SW_1` carries the owner's ruling: *"The xenotype roster is PURE Star Wars;
non-canon species are cut, not reflavored."* It was closed on a faction-side measurement — 66 of
67 non-canon xenotypes unreachable because their factions sit at
`startingCountAtWorldCreation: 0`.

🔴 **That is not the whole route.** `PawnGenerator.XenotypesAvailableFor` adds `kind.xenotypeSet`
**unconditionally**, and **106 of our own PawnKindDefs carry one**. Measured live:

```
Jawa_Spawn_Hutt        RimMandrakeHutt 7  / MandrakeJawa 5     <- a coin flip
Jawa_Gamorrean_Guard   Jawa_Xeno_Gamorrean 12 / -              <- useFactionXenotypes: false
```

⚠️ **These are OUR defs.** Nobody smuggled them in — third-party contamination was measured at
zero across 1737 PawnKindDefs. The 13 `Jawa_Spawn_*` kinds are literally named "spawn enablers",
so somebody meant them to work.

## What DECIDE has to answer, and only DECIDE

1. **Is the ruling about the roster, or about arrivals?** If a Hutt must never walk into a colony,
   these 106 kinds are in scope and the fix is `useFactionXenotypes` plus the kinds' own sets —
   ⚠️ **not** cutting XenotypeDefs, which `XENOTYPE_ROSTER_PURE_SW_1` already ruled against.
2. **Is `RimMandrakeRakata` on the vanilla `Ancient*` kinds intended?** It fires **every time**,
   through vanilla's own Ancients faction, and it is the one deterministic case.
3. **Is gene extraction / xenogermination in scope at all?** A player *assembling* a non-canon
   genotype by hand is a different act from a pawn *spawning* as one. Left **UNMEASURED**
   deliberately, because measuring it before this is answered would be work with no consumer.

⛔ CHECK does not redesign this. The live behaviour is measured and recorded; the question of what
v1 IS belongs to DECIDE (`POLICY.md > DECIDE IS A DOMAIN, NOT AN AUTHORITY`).

Evidence: `infrastructure/state/evidence/xenotype_nonfaction_routes_2026-08-26_CHECK.md`
