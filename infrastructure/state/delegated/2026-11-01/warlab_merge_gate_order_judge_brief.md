# Judge brief: the war lab gate order (delegation_policy §4, class: design)

You are the judge. You did not write this and owe it nothing. Run fresh, on opus, with no maker context.
Decide: **may `design/Jawa/worldbuilding/dungeons_arc_spec.md` §2.3 (from "The gate order" to the end of
"Who stands where") stand as the ruled gate order?** Answer KEEP, REDO or UNSURE per §4.4, for the whole
and for each hard read.

**Item criteria** (`ASSAILANT_WARLAB_BUILD_MERGE`): the gate order (the four gates of the §2.3 table) is
ruled by the owner where it is a judgement, and written once.

**Read yourself:** `design/Jawa/worldbuilding/biomes/the_chill_warlab_routes_spec_2026-09-27.md`,
`design/Jawa/worldbuilding/biomes/the_propane_lakes.md` §6 and §8,
`design/Jawa/worldbuilding/warlab_garrison_early_blast_2026-11-01.md` §5 and §6, the spec's §2.5 and §2.10.

## Owner rulings it touches, his words

- 2026-08-30: *"Perhaps utterly frozen in the cold depths until the players begin to wake/thaw it by
  bringing an old power core to its hidden location."* Same sitting, point 2: all 70 rows of the flesh sheet
  are the complex's roster (spec §2.5).
- Hard ban #8: *"The war-legacy split holds — lab guardians are mechanoid/ancient; the Assailant material
  here is the study subject, never resident weapon-fauna."* Its gloss, 2026-09-07: *"Hard ban #8 stands
  unchanged: live and dangerous under containment is not the same as resident weapon-fauna roaming the
  biome map."*
- 2026-10-10 card 5: the landing and the war lab are the same location (`canon.yml`
  `assailant_reveal_arc.site_src`).
- 2026-09-12: *"the command codes are the only way into the base after it's revealed by the melting event."*
- 2026-09-27, Route 6: *"If the Empire finds out about the place, they bomb their way into it and then get
  overrun, exposing the War Lab for player entrance without action."* And: *"Nothing the player does
  bypasses the door, but the Empire fallback does."*
- Card 8, 2026-10-10: *"…a small Imperial force will garrison outside the War Lab that must be defeated to
  enter and use the codes."*
- Delegation §2.4: *"Applying a ruling to a case it does not name is delegated; changing what it says is not."*

## Hard reads: where the maker went beyond his words

Rule on each one in turn. The list is `hard_reads` in `warlab_merge_gate_order.json`.

1. **Route 6 replaces gate 3 only.** The socket survives, and the last watch did the overrunning.
2. **Ban #8.** Is the §2.3 reading application or reinterpretation? If it is reinterpretation, say UNSURE;
   the call is his (§2.4).
3. **The clock.** Seating the core, not opening the door, starts the 15-day stasis clock.

## Recording it

In `warlab_merge_gate_order.json` set `judge`, `verdict` and `hard_read_rulings` (one entry per hard read).
On KEEP: drop PROVISIONAL from §2.3 and settle `WARLAB_GATES_DECIDE_BAN_EIGHT_ONE_READ`. On a ban #8 UNSURE,
that item stays with him and the work waits. `python3 src/RimMandrake/Utils/warlab_merge_check.py` then reads it.
