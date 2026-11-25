Never publish (./publish or any rimflow --publish write) from the clone a live modcheck runs from: the publish rebases the clone, the mod's source hash moves while the drivers run, and modcheck then reads every driver row as 'no <driver> result at the current mod hash carries this row' (FlowWorks 2026-11-25: sprinkler_live wrote 9 PASS rows at hash 0609691f, the judge read d2d19d8d after two FlowWorks commits arrived). Write notes after the run, or from another clone.
item: RIMMANDRAKE_RERUN_TWO_HARNESS_REPAIRS_ON_FREE_ARCHMAGI_GAME
home: skills/live-debugging-proof-harness
