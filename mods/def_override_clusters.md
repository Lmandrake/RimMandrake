# def_override_clusters.md — contested defNames across the 562-mod stack

_Measured 2026-08-10 with `Utils/def_inventory.py` against the resolved load set
(after the root-`Defs/` resolver fix). **Backlog note, not an investigation** —
recorded so it is not rediscovered from scratch. Nobody has audited these yet._

Regenerate with `DefSet.duplicates()`; see `Utils/README.md`.

---

## What this measures

A **contested key** is a `(defType, defName)` pair declared by more than one
active mod. RimWorld resolves these by **last in load order wins** — silently.
No error, no warning; the earlier definition simply ceases to exist.

**375 contested keys** stack-wide. Distribution:

| defType | contested |
|---|---|
| ThingDef | 69 |
| StatDef | 52 |
| FacialAnimation.FaceAnimationDef | 42 |
| TraderKindDef | 40 |
| BodyPartGroupDef | 21 |
| HediffDef | 16 |
| ResearchTabDef | 13 |
| AbilityDef | 12 |
| FacialAnimation.HeadTypeDef / LidTypeDef | 10 each |
| PawnKindDef | 8 |

For animals specifically the number is tiny and already understood — 3
(`Armadillo`, `Penguin`, `AA_Eyeling`); see `mods/inventory/README.md`.

## The two clusters worth a look — and why they are probably NOT bugs

Both large non-animal clusters trace to a **single mod each deliberately
replacing a whole vanilla subsystem**. That is a legitimate, if blunt, pattern,
so the finding is "know what is being replaced", not "something is broken".

**StatDef — 52 keys, every one `Core` vs `Stronger Quality Scaling (1.6)`.**
The mod redefines 52 Core stats wholesale, including `ArmorRating_Sharp/Blunt/
Heat` and `Insulation_Cold`. Note the overlap with our own tooling: those are
exactly the stats `animal_inventory.py` reads, so **any recalibration we do
against vanilla stat assumptions is being silently reinterpreted by this mod**.

**TraderKindDef — 40 keys**, `Better Traders` vs `Core` (32) and `Royalty` (8):
`Base_Neolithic_Standard`, `Base_Outlander_Standard`, the `Caravan_Neolithic_*`
family, and so on. Relevant because trade composition is load-bearing for the
campaign's economy and for the Hutt-Cartel/MiningCo reflavouring.

## Why it is still worth auditing later

Wholesale replacement is safe in isolation and hazardous in a 562-mod stack:

1. **It defeats other mods' patches.** A `PatchOperation` from a third mod that
   targets the Core version of a def operates on XML that the replacement then
   discards — or vice versa, depending on order. This is the same failure shape
   as the Armadillo/CWAS crash, one layer up.
2. **It is load-order sensitive and silent.** Move either mod and the winner
   changes with no diagnostic.
3. **We cannot yet see the result.** These are offline declarations. Whether the
   replacement or the original actually won is a question only a live dump
   answers.

## The concrete next step

This is exactly what the offline↔live diff is for. Once `RimDefDump` has run
once on the full stack, `modMatch=NO` rows in `divergence.csv` will name the
actual winner for every one of the 375, turning this list from "contested" into
"resolved, and here is who won". **Do not audit these by hand first** — the diff
does it for free, and by construction cannot be wrong about it.

Open questions to carry into that pass:
- Do the `Stronger Quality Scaling` stat definitions actually win? If so, every
  stat threshold in our tooling (`HEAT_HARDY`, armour comparisons) needs
  re-reading against its curve, not vanilla's.
- Does `Better Traders` win the 40 trader kinds, and does that change what the
  campaign's early economy can buy?
- Of the 69 contested ThingDefs, how many are intentional reskins versus two
  mods colliding by accident on a common name?
