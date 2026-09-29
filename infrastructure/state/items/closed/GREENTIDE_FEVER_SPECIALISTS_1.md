# GREENTIDE_FEVER_SPECIALISTS_1 — survivors become specialists: the fevers pay you back

## the ruling

**Owner, decision taken by question card, 2026-09-25 20:47** (on `GREENTIDE_RISK_REWARD_EXCHANGE_1`'s
Q1, "which new payoff do we build first?"). Recorded on the ledger:

> *"payoff category = survivors become specialists (jungle illnesses leave lasting skills/resistances,
> reusing the illness system)."*

⇒ Of ten reward categories designed in
`design/Jawa/worldbuilding/biomes/greentide_risk_reward_2026-09-22.md` §4 (R1–R10), **R1
(immunological capital) is the one to build first.** Full writeup, rationale and the ranking that put
it at #1: that doc's §4 "R1" and §4b.

## what it is

A colonist who catches one of the Greentide's fevers and survives is **permanently marked** by it, and
the mark is a **job qualification**: only a marked pawn can safely lead a deep expedition, hold a
forward camp through the wet season, or handle the freshest medicines (R2) without dosing themselves.
Unmarked pawns can still go — they just get sick, and the marked ones don't.

- **What it costs:** the fever itself. Real downtime, real deaths, a nursing burden worse than the trip
  it enables. The mark cannot be bought or rushed; a pawn who dies of it takes the investment with them.
- **Why only here:** the desert's hazards (heat, thirst, sand, raiders) are physical and leave no
  adaptation. A fever is the only hazard on the planet that teaches the body something.
- **Why it is cheap:** the hazard is already shipped — seven disease rows are live on `RM_Greentide`
  today (§1c of the design doc), delivering nothing but attrition. This category converts an existing
  transaction rather than authoring a new hazard *and* a new reward together.

## ⚠️ UNMEASURED — the two engine questions this rests on (design doc §6a, U1–U2)

⛔ The Mac has no game, no def dump, no decompiler. Do not name a field, class or value for either of
these from reasoning — confirm on the Desktop before authoring.

- **U1 — Is there a durable, mod-readable record that a pawn recovered from a given disease, and a
  hook at recovery a mod can attach a permanent immunity/mark to?** If no such hook exists, this needs
  its own condition to hang the mark off, which merges this item with `GREENTIDE_FRENZY_DISEASE_1`'s
  disease-authoring work and raises the cost from *low* to *medium*.
- **U2 — Is there a mechanism that gates a job, work type, or caravan role on a pawn carrying a given
  hediff/condition?** This is the "qualification" half. If no hard gate exists, the fallback is a
  mood/efficiency penalty on unmarked pawns rather than an outright lock.

## what already exists — do not duplicate

- **The hazard**: `RM_Greentide`'s seven disease rows (six shared with `RUT_Greentide`; see
  `GREENTIDE_FRENZY_DISEASE_1` for the in-flight replacement of two of them with "The Frenzy"). This
  item does not touch the disease list — it adds the recovery-side reward on top of whichever diseases
  end up shipped.
- **The precedent for a marked/qualified pawn state**: check `mandrake.rm.creaturebehaviors` and any
  existing hediff-as-qualification pattern before inventing a new one (none was found in the design
  pass's audit, but that audit did not exhaustively search for this specific shape).

## spec

1. **Answer U1 and U2 on the Desktop first.** ⛔ Author nothing before that — the answers decide
   whether this is a hediff-tag-and-check (cheap) or a from-scratch disease-plus-mark system (medium).
2. Design the mark as a `Hediff`/`GeneDef`-equivalent (whichever U1 points to) applied once, on
   recovery, permanent, visible in the health tab.
3. Design the qualification gate per U2's answer — a hard lock on specific work types/roles, or a
   mood/efficiency modifier fallback.
4. Name which of the Greentide's diseases (post-`GREENTIDE_FRENZY_DISEASE_1`) confer the mark. Not
   necessarily all of them — a single signature illness conferring the signature mark may read better
   than a modifier bank per disease. That is a design choice to make explicit, not default.
5. Mod Settings toggle and tuning per the standing every-mod-ships-settings rule.

## verify

A pawn who survives the named Greentide illness(es) carries a permanent, visible mark. At least one
real gameplay gate (work type, caravan role, or a stated mechanical fallback) is keyed to that mark.
No disease content is authored here that duplicates `GREENTIDE_FRENZY_DISEASE_1`. ⛔ No live-proven
claim from the Mac.

## criteria

A colony's veteran jungle-hands are visibly different from its rookies, and everyone can tell why.

## Watch out

- ⛔ **Do not re-author the disease list here.** That is `GREENTIDE_FRENZY_DISEASE_1`'s scope; this
  item is the recovery-side reward only.
- ⚠️ **The payoff must stay invisible for the first several trips** — per the owner's own accepted cost
  on the Q1 card, early deaths should read as tuition, not as the biome being unfair. Do not soften
  this by making the mark easy to earn.
- ⚠️ If U1 comes back negative, this item's cost estimate is wrong and it should be re-ranked against
  R2/R3 rather than built as originally scoped — say so rather than quietly absorbing the extra work.
