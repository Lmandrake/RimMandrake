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

## RULED, owner, 2026-08-29 — and audited clean, same session, FOUNDRY

Three questions answered:
1. **XENOTYPE_ROSTER_PURE_SW_1 covers arrivals too**, not just the choosable roster — a
   PawnKindDef bypassing faction curation to deliver a non-canon xenotype would be in scope,
   fixed via `useFactionXenotypes`/the kind's own `xenotypeSet`, NOT by cutting XenotypeDefs
   (already ruled against).
2. **`RimMandrakeRakata` on vanilla `Ancient*` kinds is INTENDED.** Leave it.
3. **Gene extraction / xenogermination is OUT OF SCOPE.** Leave unmeasured.

**Audit against the principle in (1), measured fresh — `defs.sqlite`, `captured_utc
2026-08-29T05:18:06Z`, package scope `mandrake.*`/`rimmandrake.*`:** 153 of our own
PawnKindDefs carry a non-empty `xenotypeSet` (the 2026-08-26 evidence said 106 — mod set or
dump differs slightly, not reconciled, doesn't change the finding either way). **Zero of the
153 reference a xenotype outside our own 71-def canon roster** (cross-checked field-by-field
against `d['fields']['xenotypeSet']['xenotypeChances']`, not the top-level shape a first pass
got wrong and returned a false zero on — see the session's own trail for the correction).

⇒ **The mechanism is real (Route 5 bypasses faction-level curation, confirmed) but nothing
currently exploits it to deliver a non-canon species.** Every instance is a kind named after
its forced species (`RimMandrakeBothan_Kind` → `RimMandrakeBothan`, `Jawa_Gamorrean_Guard` →
`Jawa_Xeno_Gamorrean`, etc.) — intentional identity-matching, not a leak. Per the owner's own
ruling in (1), a fix is owed only where a violation exists; none does. **No code or XML change
made — closing on a clean audit, not a build.**

## criteria
- [x] Owner ruled scope on all three open questions.
- [x] Audited: every one of our 153 xenotype-carrying PawnKindDefs stays within the 71-def
      canon roster. No non-canon arrival exists via this route today.
- [ ] Not re-audited: whether this stays true after future content additions — a one-time
      measurement, not a standing guard. Worth a `validate_patch.py`-style check if the roster
      or these kinds change again, not built here.
