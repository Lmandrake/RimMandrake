# Judge: CATHEDRAL_DESCENT_REVEAL_SITE_1 (fresh eyes, 2026-11-11)

## The statement itself
`STATEMENT.md` has two lines and neither is a claim: an empty bullet `- ` and a fragment
(`*Depends on:** item 1 ...`). wc.py turned the item's prose sections into junk bullets (already filed as a lesson,
commit e14247739e). So I judged the lines of the item file's `## verify` and `## criteria` sections
(`infrastructure/state/items/CATHEDRAL_DESCENT_REVEAL_SITE_1.md`), which are the owner's words.

- Statement line 1 (`- `): cannot tell. It says nothing. A regenerated STATEMENT.md would settle it.
- Statement line 2 (the Depends-on fragment): cannot tell. It is a dependency list, not a claim of done.

## The item's verify and criteria lines
All behaviour evidence is offline: a Python model of the trigger logic plus source-text lint of the C#
(`reveal_beat_selftest.txt`), and a generator audit plus a rendered plan of the layout (`site_selftest.txt`,
`descent_layout_topdown.png`). Nothing shows the compiled DLL running in RimWorld. I re-ran both selftests:
44/44 and PASS, which matches the evidence files.

1. Fires once, only from the ruled trigger set (dev-flag matrix: VOUCHED without flag no fire, flag without
   VOUCHED no fire): **cannot tell** in game. In the Python model it holds: sections [1] and [2] cover 72 gate
   combinations, VOUCHED-only, flag-only, Regard 1000 alone and descent-off, and each opens nothing. The C# side is
   checked only by source lint. To settle it: the dev-flag matrix run in a quicktest save, with the log.
2. Re-trigger attempts refused: **cannot tell** in game, for the same reason. In the model, section [3] covers a
   later VOUCHED poll, demote and re-climb, a quest that was opened in dev mode, and the game refusing the first
   opening. The OpeningRefusal and SpeakAddress guards are checked by source lint only.
3. No faction-visible text changes (diff the string surface): **true**. `string_surface_diff.txt` shows 3864
   strings, with the same sha, before and after every landing. The instrument can see such changes: selftest [7]
   catches a planted FactionDef string and a planted Keyed string.
4. All reveal text passes item 3's linter (scale/aliveness yes, mercy/drill never): **true**.
   `lint_reveal_text.txt` shows all four def files clean at the stage each one speaks in. A control proves the
   linter can fail: the address checked at stage 2 FAILs on 'audition'. Four planted lines (mercy, drill,
   naming, factory) are refused at stage 3, and the hardcoded C# strings lint clean. I read the address against
   arc spec §5 "In" (alive; vast, the flatness is built; salvage was cover; manners were an audition). It stays
   inside that list and says nothing about mercy, the drill or purpose.
5. Completes Oracle-absent end to end: **cannot tell** for "end to end". In the model, with no `claude` on PATH,
   the opening and the reveal both happen. Source lint shows no Oracle, process or LLM call, and fallback lines
   only. To settle it: an in-game run with no Oracle.
6. Site verified present per-slot (`jawa/list_things`, not the placement log's count): **false**. The evidence
   has no `list_things` output anywhere (I grepped evidence/). The png is a render of the generator's plan, not of
   a map. The 7 sentinels in the audit are not in the picture at all.
7. A1 lore landed in the named docs with inbound references fixed: **true** for the landing.
   `03_deep_history.md` §The Rust Cathedral (l.151-155) and §The Utinni (l.193-197), `06_the_ship.md` §The mind
   (l.55-68), and arc spec l.262-270 all link to each other. I checked l.193-197 and it is complete. Cannot tell
   whether every other inbound reference was found: that needs a repo-wide grep for the old wording.
8. Criteria: descent playable start-to-bottom on a quicktest-loaded save: **cannot tell**, with no live evidence
   at all. To settle it: the escort run from arrival to terminus in a quicktest save, with the escort's pass
   behaviour seen working.
9. Criteria: reveal flag published to the blackboard: **cannot tell** in game. Only the model's poll record
   shows it ("reveal flag published in the poll's record").
10. Criteria: stage 3 entered by this beat and only this beat: **true in the model and by source lint**
    (section [4]: `knowledge_revealed` is written in exactly two places). Not shown in game. Because I would add
    that caveat, it counts as **false** as a claim about the game.

## Staged or flattering
- The top-down png is a tidy schematic with flat colours and no pawns. It cannot show sentinels walking past, an
  escort, or that the map spawns. The production line and coolant run show up as single coloured bands.
- "dev-flag matrix" and "end to end" are met on a Python fixture ("ordinary-play fixture"), not in the game. The
  word "in game" in one selftest line ("in game (source lint)") means a grep of the C#.
- The item file itself says Seat/needs: FOUNDRY, bridge plus game-up. The live half of this item was never
  attempted on this offline seat.

would show: no
