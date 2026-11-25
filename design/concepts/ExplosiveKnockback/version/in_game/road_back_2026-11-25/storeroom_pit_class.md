# The storeroom-pit deaths (RIMMANDRAKE_CLASS_KNOCKBACK_SHELL_KILLS_COLONIST_TWO_OF_FIVE_RUNS), ArchSmall, 2026-11-25

Class: the staged scene was wrong (APPARATUS FAULT), not the mod.

- On ArchBig the two dead colonists read dead 3 and 6 ticks after the blast, before any flight lands.
- Probe `scripts/probe_storeroom_deaths.py` on the release build (DLL sha ddbf5e27c549), the fixture save, the 25-mod tier:
  knockback on 0 deaths in 4 runs, impact damage off 0 in 4, knockback OFF 2 deaths in 10 (colonist 36513: Brain
  MissingBodyPart from Shredded, Skull Crack, Shredded head, torso and stomach: the vanilla Bomb). Rows:
  `probe_storeroom_deaths.jsonl`.
- So 25 Shell_HighExplosive (Bomb 50 on a 6-cell ring) can kill a colonist in flak with no mod at all. No bar promises
  "kills nobody" (inv_killed_corpse expects a blast to kill). The scene's forbidden clause on the people is removed
  (608e5aabf2); its goods clause stays.
- The fixture records mandrake.rm.patches; without it the game refused the load ("1 mod(s) recorded by the save are not
  currently active"). The tier explosiveknockback_visit now carries it (608e5aabf2).
- The scene's plant knockback_off was never applied (a driverless settings write, refused inside a session): the planted
  run read SUCCESS at 10:48. Repaired d172734c75 (HARNESS).
- Both ways on d172734c75, ArchSmall, 2026-11-25 10:51 to 10:57 PST: real SUCCESS 4 of 4 (scn_deed97e56615,
  scn_1a470481aeeb, scn_97c96b3343ef, scn_19bb151a66cb), plant knockback_off MOD FAILURE (scn_8cd5d13d9847). Two more real
  runs gave no reading (the WSL interop timed out under load 31; no game contact).
