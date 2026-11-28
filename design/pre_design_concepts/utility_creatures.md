# Utility creatures

- **Name:** Utility creatures
- **Kind:** new mod
- **Gets:** the player orders one trained animal or droid to do one job, such as "dig this pit" or "cut that tree", and that creature does it.
- **Added:** 2026-11-26
- **From ticket:** `UTILITY_CREATURES_DESIGN_DIG_THIS_PIT_BOY` (ended 2026-11-26: this file keeps the concept)
- **Code:** none. Measured 2026-11-26 with `git grep -il "utility.creature\|UtilityCreature\|dig this pit" -- src`: no mod code. The two hits are a different thing (`WallsSlotsUtility.CreatureLine` in `D:\Luke\dev\RimMandrake\src\RimMandrake\HugeThings\`).
- **Last offered:** 2026-11-27
- **His answer:** Flesh out now with the Conductor (his card answer of 9:25 PM PST 2026-11-27: he picked 'Utility creatures' and 'Shared work spots')

## His words

- 2026-10-25 (ledger, OWNER `file` event of the ticket, 2026-10-25T14:56:28Z): "So let's make shovels and shovel creatures. Kinda begs a new mod doesn't it? Utility creatures. Creatures with commands like "dig this pit" or "cut that tree." File that idea for v2 for now. It's a good one."
- 2026-11-26 (ledger, OWNER note on the ticket, 2026-11-26T21:11:53Z): "I do like both of those ideas still utility creatures and shared interaction spot. Is there a designation or safe place for good mod ideas we haven't designed out yet?"

## Where the concept came from

The ticket's causal chain, oldest first: `BRIDGES_DIG_DESIGN_THREE_WAYS_EACH` caused `DIG_SPOIL_BUILD_GRAVEL_PAYS_ITS_WAY`,
which caused `SHOVELS_BUILD_NO_DIGGING_BARE_HANDED` (the Shovels rule: nothing digs bare-handed), which caused this
ticket. So the concept grew out of the digging and shovels work: a creature that digs uses a shovel too.

## The source ticket, whole

`UTILITY_CREATURES_DESIGN_DIG_THIS_PIT_BOY`. State `proposed`, kind `design`, needs `offline`, target `v1`, owner BENCH,
filed 2026-10-25T14:56:28Z, caused by `SHOVELS_BUILD_NO_DIGGING_BARE_HANDED`. The ticket had no prose file.

Title: "v2 idea, new mod: utility creatures — trainable animals (and droids/machines) taking commands like 'dig this
pit' or 'cut that tree'"

History (7 events):

- 2026-10-25T14:56:28Z OWNER `file`: for BENCH, kind design, needs offline, target v1, with his words above.
- 2026-10-29T01:32:13Z OWNER `reassign` to FOUNDRY (a seat now retired, since 2026-11-02). Reason: "v3 cutover: BENCH lane -> FOUNDRY". His words on the
  event: "Once we switch over to Conductor + ispatch + Foundry, all bench items get reassigned to Dispatch-> Foundry".
- 2026-10-29T04:56:21Z BENCH `note`: "Done when: a design doc under design/RimMandrake/ names the command set, which
  creature/droid classes take commands, the vanilla work-type/designation hooks used, and a v1 slice; otherwise drop as
  parked idea". Reason: "backlog deep assessment: bare v2 idea for a new mod with no done-condition".
- 2026-11-03T04:58:27Z OWNER `reassign` to BENCH. Reason: "FOUNDRY retired 2026-11-02: re-homed to BENCH (bucket
  designer)". By card: "What should happen to FOUNDRY? → Retire it (Recommended)".
- 2026-11-03T05:13:00Z OWNER `note`: "Designer bucket (FOUNDRY retired 2026-11-02): its design still needs arguing out,
  so it waits for the Designer (src/RimMandrake/rimflow/roles/designer.md, per mod, on demand). Relentless skips kind
  design/decision/decide/card until the mod has a concept tree." By card: "What should happen to FOUNDRY? → Retire it
  (Recommended)".
- 2026-11-24T05:44:38Z BENCH `home`: home `unplaced`, group `new-mod-ideas`, flag `CANNOT TELL`. Reason: "a v2 idea for
  a new mod that has no name or folder yet" (the owner's grouping by home, 2026-11-23).
- 2026-11-26T21:11:53Z OWNER `note`: "He still wants this idea (his word of 2026-11-26). Not designed, not scheduled.
  No sweep drops it as stale." With his words of 2026-11-26 above.

## Design files

- A dry-walk rehearsal: `D:\Luke\dev\RimMandrake\design\concepts\_dry_walk\UtilityCreatures\` (`sheet.md`, `plan.md`,
  `tree.json`, `log.md`). Its answers are a stand-in model's, not his, and it is not a design. What it holds, in short:
  - its root, in the stand-in's words: "you order one chosen creature to dig one chosen pit, and that creature does
    it"; "an order that cannot be carried out is refused at the click, with the reason"; "no order is forgotten
    half-way";
  - leaves: one chosen creature digs the one cell the player ordered; with no shovel in reach the order is refused at
    the click, with the reason on screen; an interrupted creature goes back and finishes the same order by itself; the
    order loop stays cheap; it is not a work priority (nothing digs without an order); a creature never digs without a
    shovel (the Shovels rule holds); waived: which kinds of creature take commands in the first version;
  - its plan: one order Gizmo on a commandable creature, a saved per-pawn order record, a JobDriver for digging that
    reuses the Shovels rule's check; the vanilla Mine designation only for the cell's state, never for job pickup;
    three designs weighed (a queued order on the pawn, chosen; a one-pawn-reserved designation; a work type with a
    whitelist, rejected); risks: a Gizmo on an animal may not draw, an interrupted-job resume collides with vanilla's
    job queue, how a creature holds a shovel is unsettled;
  - open in the rehearsal: how a creature comes to accept commands (training, or by kind). Two of its leaves are marked
    "HIS WORDS DO NOT COVER THIS: he must answer it" (refused at the click; resumes the same order).

## Offers

- 2026-11-27: Flesh out now with the Conductor (his card answer of 9:25 PM PST 2026-11-27: he picked 'Utility creatures' and 'Shared work spots')

## The design talk of 2026-11-27 (his card of 9:51 PM PST), first pass

The Conductor proposed a mechanism (an order to one creature; animals trained and droids by module; the Shovels rule
holds; refused at the click with a reason; an interrupted creature finishes the same order; a first version of one job).
Two points went to him on a card.

**How should a creature come to take orders?** He typed his own answer, word for word:

"Digging animals don't use shovels, they have them built-in. They should naturally dig by themselves as they desire. The
training allows players to induce them to work where desired. They never need a shovel. Droids receive skills and
abilities through modules and augmentation via their limbs and actuators, working together to enable the effect. Droids
take work like colonists. It is open whether they can be click-commanded like a colonist or simply work in the
background."

The options on the card that he did not pick: "Train animals, module droids (Recommended)", "By kind, no training", "A
harness makes it able", "Training and a harness".

**What should one order be?** He picked "One click, one job (Recommended)". The description, word for word: "Why: it is
a command, as you said. You click one pit square or one tree; that creature does it and is free again. Simple to build
and test. Costs many clicks for a big dig. Recommended: the smallest thing that proves the mod; a queue can follow." Not
picked: "A queue of jobs", "A work area".

What his words settle (the Conductor's reading):

- A digging animal digs with its own body. It never needs a shovel. The Shovels rule (nothing digs bare-handed) does not
  bind a digging animal.
- A digging animal digs by itself, where and when it desires, with no order. Training lets the player direct that digging
  to a chosen place.
- A droid gets a skill from its modules together with its limbs and actuators. A droid takes work as a colonist does.
- An order to an animal is one click for one job.

Open after this pass: whether a droid takes a click order or only works in the background (his own open point); what an
animal's own digging leaves on the map and how the player reads it; which animal kinds dig; whether the droid half belongs
to this mod or to the droid mod.

## The design talk of 2026-11-27 (his card of 11:59 PM PST), second pass

Three points went to him on a card. The whole card is on the ledger
(`python3 src/RimMandrake/rimflow/card_capture.py show RIMMANDRAKE_FLESH_OUT_UTILITY_CREATURES_AND_SHARED_SPOTS_HIS_PICK`).

**What should an animal's own, unordered digging leave behind?** The options were "Real holes, away from home
(Recommended)", "Real holes anywhere" and "Marks only, real holes on order". He typed his own answer, word for word:

"3+1 and also standard mountain-type mining. But this will be different for specific species of animals, these are just
the meta-rules as an example. We will need to spec out many, many kinds of utility animals and their idiosyncratic
behavior together."

**Where should droid work orders live?** He picked "Droids go to the droid mod (Recommended)". The description, word for
word: "Why: droids work by modules, like colonists, which is the droid mod's own design. Gets: Utility creatures is
animals only, small and soon. Costs: no droid digs or cuts on order until the droid mod is designed. Recommended: it
keeps two different systems apart." Not picked: "Droids stay in this mod", "Build the order here, droids join later".

**How many animals and jobs should the first version hold?** He picked "Two animals, dig and cut". The description, word
for word: "Why: your first words named both jobs. Gets: proof that the order works for more than digging. Costs: a
second animal with its art, its own unordered behaviour to design, and about twice the scenes." Not picked: "One digging
animal, 'dig here' (Recommended)", "Several digging kinds, one job".

What his words settle (the Conductor's reading):

- The rules for an animal's own digging are meta-rules. Each species gets its own behaviour from them.
- The meta-rules that he named are three. Option 3: marks only, and a real hole where the player orders one. Option 1:
  real holes, but never inside the home area. And standard mountain-type mining: an animal that mines rock as a colonist
  mines rock.
- The species are specified with him, one kind at a time: "many, many kinds of utility animals and their idiosyncratic
  behavior together".
- Utility creatures is animals only. Droid work orders belong to the droid mod.
- The first version holds two animals and two jobs: one that digs and one that cuts trees.

Open after this pass: which two animals come first; for each species, which meta-rule its own digging follows; what
unordered behaviour the tree-cutting animal has; how the player reads each behaviour on the map.
