# RIMMANDRAKE_TEACH_OFFLINE_MODEL_FIRST_BUILD

## spec
The owner, 2026-11-17 ~10:50 AM PST: "Also, it feels like the Fable Rescuer again found that offline modeling is
REALLY informative and useful. Sounds like something that should be instructed to the mod builder in general, yes,
from the get-go? I kinda thought we already had, but maybe it hadn't had a chance to benefit from that yet."

Measured 2026-11-17 (grep): the offline-model instruction (a generator of the situations the mod can be in, read by
the bars' own checks, its range declared) lives only in `src/RimMandrake/rimflow/roles/fable_rescue.md` step 2 and,
as an instrument choice, in `roles/designer_cleanse.md`. The ordinary offline builder brief (`maturation.brief_text`)
and the road-back fixer brief (`maturation_autonomy.fixer_brief`) carry `HOW_A_BAR_HOLDS` (write down the range, read
it with the bar's check) but not: keep the decision logic Verse-free so an offline test compiles and runs the SHIPPED
decision (the Explosive Knockback rescue's `RM_KnockbackPlan.cs`, ~122,000 enumerated lanes); build the generator
before fixing or tuning; declare what it varies, how many cases, what it leaves out; a mod with no decision logic says
so in one line.

Fix: one shared source, a marked block in `roles/fable_rescue.md` step 2 that the rescue brief reads in place and
`maturation.OFFLINE_MODEL` reads at brief time; `brief_text` and `fixer_brief` carry it. No spend, cap or budget in it.
Ruling recorded in `design/RimMandrake/standing_rulings.md`; one line in the Maturation Pipeline spec.

## refs
file: src/RimMandrake/rimflow/roles/fable_rescue.md
file: src/RimMandrake/rimflow/maturation.py
file: src/RimMandrake/rimflow/maturation_autonomy.py
file: src/RimMandrake/rimflow/selftest_offline_model_rule.py
file: design/RimMandrake/standing_rulings.md

## criteria
- The offline builder brief and the road-back fixer brief carry the offline-model instruction, read from one source.
- The rescue brief (`roles/fable_rescue.md`) still carries it, in place.
- No spend, cap or budget is stated in it.

## verify
`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_offline_model_rule` fails on the base (no
`maturation.OFFLINE_MODEL`, no marked block) and passes after: the builder brief (`brief_text`) for a mod contains the
block, the road-back fixer brief does too, `fable_rescue.md` still contains it, the text exists once in the repo's
brief sources (no second pasted copy in any .py or role file), and it names no spend, cap or budget.
