# RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST

NEXT: admitted; nothing launches for WreckedMachines, the Designer included, until he says go (his hold below).

## his hold (2026-11-19 ~9:05 AM PST, relayed by the Conductor)
"Do not yet run the Fable-only passes... we don't know if the Pipeline is really ready, and this is a very expensive
test."
So WreckedMachines is admitted and no pass runs: no Designer run, no build, no in-game stage, whatever the readiness
list reads. Only his own go lifts this. Seeding, `designer_stage.py init` and the readiness list stay allowed only
after `./pipe off WreckedMachines` (a newly seeded mod reads ON; the orphan sweep no longer starts a concept no run has
opened, and `pipe off` now takes the unseeded mod: `RIMMANDRAKE_HOLD_NEW_CONCEPT_DISABLED_DESIGNER_CHAINS`).

## spec
The owner, 2026-11-19 ~8:35 AM PST, in answer to the Conductor's recommendation "say 'Wrecked Machines on Fable' now as
the admission. I then build its readiness list, and the pass starts by itself when the list reads READY":

"Ok, Wrecked Machines it is. It has a generic possible implementation and then the Utinni-specific weaving it into the
god-ship concept. First decision would be whether we even bother with the generic version. I suspect it's a good,
strong concept save for the much larger lift in terms of art generation, but we're pretty good at that. Then the Utinni
specialization would bring in the holy aspects of repairing the work. Could even be extended to ship components and
things. Needs a LOT of work using our modern Design passes of course, we didn't have anything like that before."

This item admits WreckedMachines to the Maturation Pipeline (`design/specs/2026-11-13-maturation-pipeline.md`) as the
"Fable from the start" experiment: one mod built start to finish on Fable 5.2 and compared with an Opus 5.5 build of a
similar mod (Graffiti is the proposed control) on cycles to a green certificate, in-game failures and weighted tokens.
Background: `D:\ClaudeWork\rimmandrake\conductor\card_drafts_20261117.md` section "CARD B"; it discharges
`RIMMANDRAKE_REASK_FABLE_FROM_START_WHEN_MOD_IS_FREE`. It replaces `WRECKEDMACHINES_DESIGN_FIRST_TOUCH` (a first-touch
Designer pass filed 2026-11-04 for the retired Relentless loop): this item is now WreckedMachines' first-touch Designer
item, as `RIMMANDRAKE_ADMIT_CONTAGION_AS_NEXT_BIOME` was Contagion's.

## the Conductor's reading (delegated calls, never his words)
1. The generic, franchise-free WreckedMachines (RM_ tier, `mandrake.rm.wreckedmachines`) is the mod Fable takes, Design
   Version 0.1.0. His "I suspect it's a good, strong concept" is the evidence. The Designer's first pass still states the
   case for and against a generic version in its design text (his "First decision would be whether we even bother").
2. The Utinni specialization (the holy aspect of repair, woven into the god-ship) is a separate designed part in the
   RimUtinni tier, designed after the generic design settles: `RIMMANDRAKE_DESIGN_UTINNI_HOLY_REPAIR_AFTER_GENERIC`.
   Not part of 0.1.0's bars.
3. Extending repair to ship components is Divergent, a ticket for the next version, never moving 0.1.0's bars:
   `RIMMANDRAKE_EXTEND_WRECK_REPAIR_TO_SHIP_PARTS_NEXT_VERSION`.
4. The existing design and code predate the modern Designer passes: `src/RimMandrake/WreckedMachines` (81 files, 1,818
   C# lines, last commit e08969370e 2026-11-11), `DESIGN.md`, `MACHINES.md`, `V2.md`, and the north star
   `design/validation_walks/RimMandrake/WreckedMachines.md` (14 walk steps). The Designer starts from the concept and
   treats that text as input, not as settled.

## the route (what admits it; each step is the Conductor window's act or its launch, not a helper's)
There is no `design/concepts/WreckedMachines/` folder and no stage record yet, so `./pipe show WreckedMachines` lists
no consumables ("no mod 'WreckedMachines' in the pipeline"); `./pipe off WreckedMachines` works (its shipping folder). As Contagion's admission did (b38ed346e9), with a hold first:
0. `./pipe off WreckedMachines --why "his hold 2026-11-19 ~9:05 AM PST: no Fable pass until he says go"` before
   anything below (see his hold above).
1. Write `design/concepts/WreckedMachines/journal.md` (Stage now: Intake), `version/VERSION.json` (0.1.0, open) and
   `stage.json`, then `python3 src/RimMandrake/rimflow/maturation.py seed WreckedMachines`.
2. `python3 src/RimMandrake/rimflow/maturation.py advance WreckedMachines --to designer --by BENCH --why "admitted on
   his words, item RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST" --owner-said "<his words above>"`
   (clause `intake_closed` passes on his words).
3. `python3 src/RimMandrake/rimflow/designer_stage.py init design/concepts/WreckedMachines --mod WreckedMachines --item
   RIMMANDRAKE_ADMIT_WRECKED_MACHINES_FABLE_GENERIC_FIRST`
4. `python3 src/RimMandrake/rimflow/role_launch.py run-now --role Designer --concept design/concepts/WreckedMachines
   --apply` only after he says go, with the readiness list reading READY for the design stages and `./pipe on
   WreckedMachines` citing it. A READY list alone does not start it.
Running every stage on Fable is not possible today without a change: see
`RIMMANDRAKE_PIN_MOD_MODEL_FABLE_EVERY_STAGE_ROLES_OPUS`.

Readiness list: `D:\ClaudeWork\rimmandrake\conductor\pipeline_ready_for_wreckedmachines_20261119.md`.

## criteria
WreckedMachines is in the Maturation Pipeline at Design Version 0.1.0, Stage 1 (the Designer), moved from intake on
his words above; its Designer run is on Fable 5.2 (`claude-fable-5-2`).

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/maturation.py show WreckedMachines` reads "0.1.0: Stage 1, the
Designer" with a move from intake carrying his words, and `./pipe show WreckedMachines` lists the mod; the Designer
run's unit records model `claude-fable-5-2`.

## What the card said

<!-- answered 2026-11-27T04:58:31Z; recorded by `note` (OWNER); written by rimflow, never by hand -->

**Question:** Wrecked Machines, Designer question 2 of 3. Picture a stranger's colony in an ordinary game, a year in. The note of your card of October 3 says relics are found at ancient ruin sites; it does not say 'only'. In an ordinary game those ruins exist only on map tiles that carry the ancient-ruins feature. The answer decides which placement code gets built. There are two options because the Designer's third is 'something else you picture': type it on the write-in line. When does the mod first show itself?
**Picked:** Ruins, plus a rare wreck (Recommended)
**Its description:** Why: every colony meets the mod, even one that never leaves home. Buys: now and then one half-buried wreck on an ordinary map, there on arrival; the ruins hold the good ones. Costs: a wreck is less rare. Recommended: it is the Designer's pick, on the test 'does a stay-at-home colony ever see the mod'.
**Other options:** Only in ancient ruins
