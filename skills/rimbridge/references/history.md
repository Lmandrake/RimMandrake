# History: evidence and old lines that left `SKILL.md`

The lessons are in `../SKILL.md`. This file holds only the old figures and the lines that are no longer true. Git holds
the rest. Each line below is a record, not a rule.

## Where to go, and connecting (§0, §1)

- Until 2026-11-23 the preflight row of §0 said "fold-in owed: full text lives there until a curation pass". The curation
  pass of that day kept the text in `preflight.md`: each row of that table is a pointer.
- Until 2026-11-23 the §1 command began with `python`, against the rule in the same section (`python.exe` from WSL). §1
  also called port 5174 the port of the bridge; 5174 is ArchBig's, and ArchSmall has 5175.

## Claiming a game (§0b)

- Until 2026-11-23 the example typed `game_lock.py claim a` and `release a`, and the start command was
  `launch b --wait`. Both keys still work; people now type ArchBig and ArchSmall.
- Until 2026-11-23 a bullet said that the 45-minute staleness rule measures EVENT SILENCE, not game activity. It told a
  driver to emit a periodic note in a long session. The driver lock of 2026-11-21 (`game_lock.py`) keys a holder on its process, so event
  silence decides nothing.
- Until 2026-11-23 `connect-and-claim.md` told a refused driver to wait for the release, or to check with the owner if the
  hold looked abandoned. A dead holder's game is free now, so there is nothing to ask.

## Census and counts (§5, §9)

- §5 once counted 15 of the companion's tools as map-scoped. §9 once said "all 91 `jawa/` tools" (2026-08-19). Counts
  move: recount (SKILL.md §1).

- Five bullets stood under "four … one-way doors" in §5. Commit history shows that the inhabited-harness bullet was added
  later (2026-09-23), so it now stands outside the four.

## Defs, time and mod lists (§3, §4, §6)

- The §3 row "spawn a pawn" and §4 once gave `Actions\Spawn Pawn...` with no condition. `traps/pawns-factions.md` records
  that it NPEs on every pawn defName on a VEF-loaded list.

- §3 once named a 19-mod minimal list for the 22 s restart. The 22 s was measured on the 13-mod list of 2026-08-19.
- §3 once said "Long runs are risky (owner, 2026-10-13)", and later "No long runs". His card of 2026-11-23 is the rule:
  "Allowed when the colony is safe" (`design/RimMandrake/debug_process.md` § "A long clock advance"). His words of 2026-10-13:
  *"Do not do this long run now. Go back to building and testing things you can directly measure. No more long runs."* (the ledger event of 04:34Z; in the
  transcript the words go on: *"No more long runs, ok?"*)
- §6 once called `--tier bridge` a list of 3 mods, and said "Three suspects instead of
  five hundred". On 2026-11-23 the plan listed 10 entries: Core, the five expansions, Harmony, RimBridgeServer, Cherry
  Picker and SimpleCameraSetting.
- §6 once said that `modset_builder.py --restore` hands back the PREVIOUS TIER after a chain of tiers, for example
  xenotypes(16 mods) → beastmechanics: the backup then held only 16 mods (2026-09-20). It told the reader to pick the
  backup whose count matches the full list, and to restore ModsConfig before releasing the bridge (owner list 547 mods,
  md5 1f7122ea...). Commit `7de700be43` (2026-10-12) brought the swap marker and the md5-verified restore;
  `0a63b2267e` (2026-10-15) hardened it. There is no "restore before release" step now (root `CLAUDE.md` §Facts you
  cannot guess).

## Speed (§8)

- §8 once cited §5's "compose the sequence into a script and run it once". §5 does not hold that line. §8 now states it.

## Measuring damage (§2)

- §2 once called a `.rws` parse "the only way to measure damage". `jawa/pawn_get` returns the first 40
  hediffs of a spawned pawn: def, part def and severity (`JawaBenchPawnTools.cs`). It does not tell left from right.

## Shipped docs (§7)

- §7 once said that the full MIT source sits in `vendor/mod_sources/RimBridgeServer-main/`. On 2026-11-23 that folder
  held docs, tests, tools and the built DLL; the mod's own source folder was absent.
