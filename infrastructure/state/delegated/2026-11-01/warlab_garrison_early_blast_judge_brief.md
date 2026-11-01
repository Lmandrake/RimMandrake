# Judge brief: the early lake blast design (delegation_policy §4, class: design)

You are the judge. You did not write this design and owe it nothing. Decide one thing: **may this
note stand as the ruled design for its item?**

**Artifact:** `design/Jawa/worldbuilding/warlab_garrison_early_blast_2026-11-01.md`

**Item criteria** (`WARLAB_GARRISON_DESIGN_EARLY_BLAST`): how much Empire heat rises and through
which existing heat system, with no second heat meter; the garrison's composition, siting at the
revealed lab, and persistence until beaten; and that the codes cannot be used until it is beaten.

**Governing documents, read them yourself:**
`design/Jawa/worldbuilding/biomes/the_chill_warlab_routes_spec_2026-09-27.md` (§Route 6, §Rulings,
and how Route 1 blows the lake), `design/Jawa/worldbuilding/biomes/the_propane_lakes.md` §8,
`design/Jawa/worldbuilding/ashfall_research_base.md` §6,
`design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md` §4,
`design/Jawa/story_sitting_cards_2026-10-10.md` (rulings, rounds 2 and 3).

## Owner rulings it touches, his words

- Card 8, 2026-10-10: *"Blowing up the lake early (harder than you think, but possible) will reveal
  the War Lab even if it cannot be opened yet. Then the Empire's heat will significantly
  increase,and a small Imperial force will garrison outside the War Lab that must be defeated to
  enter and use the codes."*
- Card 9, 2026-10-10: *"1+2+map change"*.
- Route 6, 2026-09-27: *"If the Empire finds out about the place, they bomb their way into it and
  then get overrun, exposing the War Lab for player entrance without action. Most violent and
  escalates the Empire maximally against the player too."*
- The door, 2026-09-27: *"Nothing the player does bypasses the door, but the Empire fallback does."*
- The key, 2026-09-12: *"the command codes are the only way into the base after it's revealed by
  the melting event."*
- The crater: *"if they fail to do so, there may be automated ways for it to occur too... no one
  will miss it"*.
- Route 6, shape: *"The route nobody buys, nobody places and nobody arms"*; lit by *"plot points, not
  just player behavior"*, Paths A and B; leaks are discrete named events, *"prevented, never undone"*.
- Strike or dive, 2026-10-12 (`dungeons_arc_spec.md`, ledger `CRADLE_STRIKE_RECONCILE_WITH_LAB_DIVE`):
  *"one or the other — strike (full Cathedral trust, lab lost) OR go in and defy the Cathedral."*
- Standing: no worldgen of any kind; a biome of ours on 0 tiles is expected, not a defect; every DLC
  is assumed; every mod ships Mod Settings.

## Rebuttal: this is round 2 (delegation_policy §4.5, your verdict stands)

Round 1 returned REDO. The maker does not contest it; every defect was taken and fixed. The record is
`infrastructure/state/delegated/2026-11-01/warlab_garrison_early_blast.json`, field `judge_rounds`.

- **Defect 1, strike and defeat left Route 6 live.** Fixed by a second state, `labFate`, and one guard,
  `Route6Live`: §4 tables, §6. A strike sets `Lost` and nothing reopens it.
- **Defect 2, every blast lit Route 6.** The clock is deleted, with its setting, and the sentence added to
  the routes spec is removed. The question is filed for him as `WARLAB_ROUTE6_ASK_DOES_LAKE_LIGHT_FUSE`,
  and the design stands whichever way he answers. What is left of the tension is said in §6.

## Hard reads: where the maker extended beyond his words

1. **`Route6Live` is false on `Open`.** Round 1 asked for cancellation on `Lost` and on a defeated
   Empire. The note also cancels Route 6 on a lab the player already opened, because no door is left.
   Is that fair, or a further change to a ruled route?
2. **The garrison reading in §6:** it guards a crater and a door and does not report what is behind
   it. Does that hold beside *"The Empire learns the place exists"* until he answers?
3. **Both §4 tables:** can every row be reached and left as written? Does any path give both a strike
   and a dive? §2's floor no longer cites a leak; does it still stand?
4. **Heat on every blast, not only an early one**, which the note itself calls an agent's reading.
5. **A blast with the codes in hand posts no garrison.** Card 8 ruled only the early case.
6. **Codes usable only on the lab's map**, which settles a question the item XML left open.
7. **The numbers:** +80 Visibility, floor 2, 12 pawns, 1,314 points. Does "small" and "significantly"
   hold? All are marked PROVISIONAL.

Also check: any second heat meter, any worldgen by another name, any softlock, any state in the
garrison table the text does not reach or cannot leave, and any cited engine fact that the source
contradicts.

## Your return

`KEEP` the note, or `REDO` quoting each violated constraint and its source, or `UNSURE` where the
written constraints do not decide it. A provisional number the maker labelled is not a REDO unless
it contradicts a ruling. Write your reasons so the next worker can act on them without you.
