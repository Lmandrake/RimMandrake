# BENCH live checks round 1, 2026-10-13 (owner: "Live checks now.")

Code at **1bf84c0efe**: `git archive` on ext4 for the deploys and the companion build, plus a python-only copy at
`D:\Luke\dev\_rmscratch\bench_live_20261013d` for `python.exe`. The helpers' uncommitted Pyrelands and companion edits
were NOT deployed.
- **Deploys:** FlowWorks deployed 2 files (DLL + srchash; the game copy was the older 00:10 build) and VERIFIED.
  PyrelandsMechanics was in sync. The composed biomes (Pyrelands) were in sync apart from one game-only png.
  The `-` lines (FlowWorks textures, old result JSONs) were kept, not pruned.
- **Companion:** JawaBench was rebuilt from the export (`build.py --gm --apply`). Census: 396 of 397 registered;
  `jawa/revoke` is missing, probably a name quoted in description prose (see the rimbridge skill), and it was not traced.
- **Tier:** ratchet_pilot+patches, 23 mods, all five DLCs (`ModsConfig.ratchet_pilot_plus_patches.xml`, md5 0bab16fa).
  Launched through Steam and READY at about 05:09 PDT.
- **Owner list:** the owner's ModsConfig was restored after the checks (md5 ee01dae9e30d121c78d88e474dacd8e8 =
  `ModsConfig.owner_before.xml`). **Round 2 must re-apply the tier before it restarts.**
- **End state:** game left UP on the Pyrelands site r1, bridge released.

| item | check | result |
|---|---|---|
| POND_RETURN_LEG_BUILD_WATER_GOES_HOME A1 | `pond_channel_probe.py`, fresh quicktest. The route: 6-cell shallow pond -> pump1 draw -> tank (45 u) -> pump2 Pour -> dug channel B (3 cells D2, 6 levels) -> pump2 draw -> tank -> pump1 Pour -> pond. Only one pump on at a time (flick) | **PASS**. L0 ledger read 60.000 at all 6 reads. The wet set equals the snapshot, the pond is back at 12/12 with receded 0, and the tank ends at 0 (`pond_channel_1.json`) |
| same, A2 | Draw down again, then put a drafted colonist on bed square s1, a PowerConduit on s2 and Steel on s3. Turn refill on at x300 (COMPRESSED, restored afterwards) | **PASS**. s1 and s2 stayed Mud while the other 4 re-wet and stock reached 12/12. The Steel moved from s3 to dry shore (151,46). After the pawn walked off and the conduit was destroyed, s1 and s2 re-wet |
| same, A3 | recorded from the night run at d01603a685 (`Transient/night_20261013/fw_live/dugbed_3.json`) | PASS. The item is **done**. Caveats: this was the short form (6 cells, not ~20), and the hose Outflow-end Body outlet was not exercised live |
| PYRE_SITE_FOOD_REPAIR_COLONY_STARVES A1 | fresh site r1 (`northstar_site.py --tag r1`, food cache 108 packs); 12 short chains (`pyre_short_r1.log`); then `colony_fed.py` | **PASS**. 13 rows PASS, including animal_distribution_correct. Every vitals note read 3 colonists with damage []. After the rows all 3 were alive and Fed (0.304). The eat probes then ran 14k governed ticks: the colonists slept, went Hungry, walked to the cache, ate (packs 108->105) and ended at Food 0.96 (`eat_probe_*.json`). The item is **done**. Short rows only, no full run |

First Pyrelands attempt REFUSED by preflight (`deployed_matches_repo: not deployed Mods\Pyrelands`): my python-only copy
lacked `src/RimMandrake/Biomes.compose.json`, so the driver did not know Pyrelands is composed. HARNESS (mine), fixed by
copying it; nothing ran (`pyre_short_r1_refused.log`).

Threats: none. Letters on the site were the cinderfall row's own stimulus (ThreatSmall "Cinderfall") and the builder's
"Inhabitants abandoned" (quicktest colony retired). Player.log 0 exceptions. No TESTENV item filed.
Heatstroke on the site colonists rose 0.009 -> 0.065 over the rows (the 56 C biome itself), noted only.
