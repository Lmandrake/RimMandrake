# Review save: PYRELANDS_REVIEW

A later session that must show Pyrelands to the owner starts from this save. It is the walk save of Pyrelands 0.1.0, which he
passed on 2026-11-24 (tag `mod/Pyrelands/v0.1.0`), plus one pen for each of the 16 creature kinds with six animals in each.

- **Savegame:** `PYRELANDS_REVIEW.rws`, 26,585,426 bytes, sha256
  `de9e52ddc8e8458c1efc3c0c7cda3999118ef645d08d8562be4d11c208cedbb9` [measured 2026-11-24 7:40 PM PST]. Three byte-equal copies:
  - ArchSmall: `D:\ClaudeWork\rimmandrake\instances\b\Saves\PYRELANDS_REVIEW.rws`
  - ArchBig: `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\PYRELANDS_REVIEW.rws`
    (this replaced an older `PYRELANDS_REVIEW.rws` of 2026-09-17; that file is kept in the backup below)
  - agent storage: `D:\ClaudeWork\rimmandrake\review_saves\Pyrelands\PYRELANDS_REVIEW.rws`
- **Label sidecar:** `PYRELANDS_REVIEW.txt` in each game's `JawaBenchReviewSigns` folder (the storage copy is
  `PYRELANDS_REVIEW.review_signs.txt`). The sign books are in the save itself.
- **It is the same bytes as** `PYRELANDS_0.1.0_CREATURE_PENS.rws` (ArchSmall), saved 2026-11-24 7:20 PM PST.
- **Mod list:** the Pyrelands small list, `design/concepts/Pyrelands/version/small_list.json`. Check it with
  `python3 src/RimMandrake/Utils/small_list.py check`. It loads on ArchSmall as saved; on ArchBig, put ArchBig on that list first.
- **Backup of both Saves folders before the copy:** `D:\ClaudeWork\backups\saves_before_pyrelands_review_20261124T1931\`.

## What it holds

- The five walk stations of `arrival_2.md`, each with its sign book: 1 burn front, 2 creatures, 3 scorch-fruit, 4 roofed grass,
  5 charred ruin. Storyteller Cassandra on Peaceful.
- A block of 16 stone pens at x 158-243, z 148-199, away from the stations. Each pen has granite walls, no roof, one door on its
  south side, and a sign `SIGN pen: <label> (<kind>)`. Each pen holds six wild animals of one kind: three male, three female,
  one juvenile and one baby, all facing south.
- The kinds: RM_FireHawk, RM_FurnaceBeast, RM_Ullai, RM_Emberscythe, RM_Sytheclaw, RM_Barbslinger, RM_FireWasp, RM_Flamefang,
  RM_Ashwallow, RSW_Anooba, RSW_Iriaz, RSW_Nuna, RSW_Orray, RSW_Zeer, RSW_Dalgo, RSW_Gizka. The owner looked at these pens and
  approved the art of all 16 (ledger event OWNER:1795577154427018698).
- The game was saved paused. Its log since the load held 0 errors.

## How to make it again

1. Load `PYRELANDS_0.1.0_VISIT9_WALK` on a game with the Pyrelands small list, paused.
2. `python.exe design\concepts\Pyrelands\version\in_game\visit_9\scripts\walk_restage.py <NAME>` places the station signs, sets the
   storyteller, stages the pens (`src\RimMandrake\Utils\modcheck\walk_pens.py`, called by the script) and saves as `<NAME>`.
3. Or, on any loaded Pyrelands walk save: `python.exe src\RimMandrake\Utils\modcheck\walk_pens.py --mod Pyrelands --stage --save <NAME>`.
4. Read a save's pens back: `python.exe src\RimMandrake\Utils\modcheck\walk_pens.py --mod Pyrelands --check`.

Run python.exe after `eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"`, with the game claimed
(`game_lock.py run ArchSmall --for "<what>" -- <command>`). A save made again has other bytes and another sha256.
