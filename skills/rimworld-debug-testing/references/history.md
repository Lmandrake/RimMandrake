# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only old figures, incident text and lines that are no longer true. Each
line is a record, not a rule. The rewrite was on 2026-11-23.

## Head: the map that nobody needed

- The head once gave the cost of a quicktest colony as **~30 seconds** (also §6). The measured range is now in §1.
- The head once said that one game is shared by both windows. There are four games now.
- On 2026-08-13 four seats sat idle. They waited for the owner to generate a world, with tests that needed *a* map and not
  *the* map. One of them was the only possible proof that `JawaIonWeapons` works. A seat had hoarded it for weeks as a
  scarce-session item. It never needed the campaign. That day is why the ruling on dev colonies exists.

## §1

- §1 once said that a shared lifecycle wait is PLANNED and that about 57 copied ready loops were in the tree.
  READYWAITS_UNIFY_ONE_HELPER closed on 2026-11-05 (PST), and `READYWAITS_MIGRATE_REMAINING_52_COPIES` is also closed.
- §1 once said that `start_debug_game_ready` itself discards the current map. From a loaded game the call waits 280 s (`validation_v2.py`,
  2026-10-02), answers `A game is already loaded.` and keeps the old map (`prove_quicktest_world.py`, 2026-11-03). `go_to_main_menu` is the step that drops the map.
- §1 once said "**Announce before calling it, and check nobody is mid-audit.**" The driver lock answers that now.
- §1 once said: never call `start_debug_game_ready` on the full list. The call worked there on 2026-09-27 (629 mods,
  `design/RimMandrake/bridge_debugging_system.md`), and the owner's final verification pass uses the whole list
  (2026-11-02).
- The exceptions of 2026-09-12 were "real, reproducible" in the old text.
- The loop of seven was measured on a worldgen sweep script that has been deleted.
- §1 once said to prefer world or map generation when nobody is at the keyboard. The owner's ruling of 2026-10-30 struck
  his presence at the machine as a condition (`design/RimMandrake/standing_rulings.md` §The bridge is passed through one
  file).

## §3 to §6

- §3 once said that this section protects the campaign save, with no word on the canonical world saves. Those were frozen
  later (2026-09-12).
- §4 once said that the `JawaIonWeapons` user-string heap is four bytes. The committed DLL, read on
  2026-11-23, has a heap of 4,596 bytes.
- §4 once quoted root `CLAUDE.md` as "do not live-test a flyer's flight without a human present". The present text names
  the owner.
- §4a once counted two screenshot traps and listed three. §5 once counted three shapes and listed four.
- §6 once called a slot of the full load a 25-minute slot. Load times are in `rimworld-load-round` §0.
- §8 once cited `DOC_BUDGET.md` for "ask what your check would print if the thing were broken". That file is gone.

## Keeping this skill honest

- Two of the rulings that produced §5 were the writer's own, and were confidently wrong for an hour (the old text
  said "today", in a file of 2026-08-13).
