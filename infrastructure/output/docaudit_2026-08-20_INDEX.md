# Documentation audit — 2026-08-20

Four parallel audits of the 258 tracked `.md` (76,779 lines). Read-only; nothing merged.

| area | report | verdict |
|---|---|---|
| faction cluster | `docaudit_2026-08-20_factions.md` | 9 files → 6; **9 contradictions** |
| state + run sheets | `docaudit_2026-08-20_state.md` | 14 files → 8; the 3 pre-load gates are **1.5 jobs** |
| skills | `docaudit_2026-08-20_skills.md` | no skills merged; **7 contradictions**; README generable |
| design (excl. factions) | `docaudit_2026-08-20_design.md` | 105 → ~96, only −4%; **21 contradictions** |

## 🔑 The finding that reframes the request

**The corpus is not bloated with FILES. It is bloated with SECOND COPIES OF NUMBERS.**

Deleting documents would save almost nothing — the design auditor's best case is −4%.
The cost the owner is feeling is not storage and not reading; it is that **one fact
costs four edits**, and when someone makes three of them, the fourth becomes a lie that
a later seat acts on. Roughly **40 live contradictions** were found across the four
audits. Every one of them is a fact that was updated in some of its homes and not all.

Worked examples, all measured today:
- The **mod count** is stated nine different ways across 15 places (570 → 587). The true
  value moved 578 → 576 → 577 inside eleven minutes. **No document can hold this.**
- The **owner's worldgen ruling** is byte-identical in **seven** state files — 175 lines
  of one 25-line ruling — and already canonical in the auto-loaded `CLAUDE.md`.
- **8 of 11 religion names disagree** between the roster and the spec; 5 contradict the
  shipped XML.
- **`loadBottom`** was documented two opposite wrong ways inside ONE skill, and the
  correction made on 2026-08-19 reached neither until today.

## ⚠️ The write-once lead was false, and that is worth recording

75 files have a single commit. It looked like the cheap win. It is not: commit
`7e98004` ("repo re-initialised, history archived") added 204 `.md` in one go, so
write-once means **dormant since 2026-08-13**, not **written carelessly**. Of `design/`'s
25, only **6** are genuinely abandoned, absorbed or orphaned; 19 are finished and correct.
Nine were committed TODAY as an active series. **Commit count is not evidence of death.**

## 🔴 The most dangerous single item found

`design/Jawa/worldbuilding/tidally_locked_world.md:152` asserts **"LATITUDE IS THE AXIS"**
with no correction banner. `ASHKARR_WORLD_DEFINITION.md:52-78` disproved it from the game's
own C# — the gradient is point-keyed, correlation **−0.98 vs +0.10**. **Two running
scripts read the wrong file.** This is not a tidying item; it is a defect in the one map.

## What actually pays

| fix | cost | saving |
|---|---|---|
| Settle the ~40 contradictions | rulings, not edits | removes wrong answers seats act on |
| One-fact-one-home + pointers | ~45 edits, once | mod count 15 sites → 0; cold load 20 → 1 |
| Generate `skills/README.md` from frontmatter | small script | kills 11 of 16 commits/yr on that file |
| `doc_budget.py`: add `infrastructure/state/*.md` | one line | **2,596 lines currently unmeasured** |
| Merge `faction_stage3_buildable_spec.md` → `FACTION_SPEC.md` | 12 rulings | the only merge that deletes wrong answers |

⛔ **What must not be merged:** owner rulings not recorded elsewhere; measured evidence
carrying a commit hash; `pawnkind_roster.md` and `faction_religions_spec.md` (machine
inputs — `gen_pawnkind_roster.py`, `validate_ideoligion.py --md` and `design_doc_render.py`
read them by path).
