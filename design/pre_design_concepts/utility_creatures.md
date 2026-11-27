# Utility creatures

- **Name:** Utility creatures
- **Kind:** new mod
- **Gets:** the player orders one trained animal or droid to do one job, such as "dig this pit" or "cut that tree", and that creature does it.
- **Added:** 2026-11-26
- **From ticket:** `UTILITY_CREATURES_DESIGN_DIG_THIS_PIT_BOY` (ended 2026-11-26: this file keeps the concept)
- **Code:** none. Measured 2026-11-26 with `git grep -il "utility.creature\|UtilityCreature\|dig this pit" -- src`: no mod code. The two hits are a different thing (`WallsSlotsUtility.CreatureLine` in `D:\Luke\dev\RimMandrake\src\RimMandrake\HugeThings\`).
- **Last offered:** never
- **His answer:** none yet

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
