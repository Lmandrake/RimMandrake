# Pyrelands progress

**Blocked on the owner for test tools:** the bridge's test-tools grant lapsed at 14:46Z on 2026-11-07, so `jawa/safe_advance`, staging tools and the suite's clock steps are refused (`ralph/QUESTIONS.md`). Do not renew it yourself: `companion_grant.json` says that is not an agent's call. Reads, `rimworld/set_time_speed` and screenshots should still work; reads were tested after the lapse, speed and screenshots were not. All deployed code is committed.

## What I saw
- **Grass does not strip.** Map `d`: 50k plants fell to 20k with up to about 3,900 fires, then back to 48k about half a day later. Fronts run several at once across the map. That count includes sprouts, so scar greening still needs eyes.
- **Tick cost during burns:** about 21 ms per tick at thousands of fires, about 10 ms in regrowth with few fires. Explosive Growth looked like up to half of that in a noisy A/B. Slower than speed 1 at the peak. Not solved, not yet written up for the owner.
- **`RM_VolcanicAsh` is not a bug:** it is the "ash storm", added on purpose by `UtinniPatches/Patches/AshStorms_Pyrelands.xml`, not rain.
- Pods, a charred ruin, the pond's soil ring and a domed ashwallow in fire all look right at play zoom (`sc_pods`, `sc_ruin`, `sc_pond`, `sc_burrow_3`).
- Unmanaged colonists get burned, and heatstroke starts within a day at 54C. They walk far off, some to study pods for the shade-cloth lesson. Still no real base has been played.

## Fixed
- Harvest left a 1% pod that regrew and could be picked again (`harvestAfterGrowth`). A harvest now takes the pod.
- The pod's rot-on-long-tick exception (theory confirmed by reading the source; `Plant_ScorchFruitPod`). Not re-observed live.
- Fire-hawk 0.15 to 0.5 and ashwallow 0.18 to 0.4: no hawk on about 5 maps, then 3 hawks on the next. Map `e` then had 9 grazers against 13 predators (4 of them big), so check the grazer line.
- Burrowers show "Burrowed!" and an inspect-pane line. **Built and deployed, never seen live.**
- Suite: harvest row (interrupting order, checks the pod is gone), dome row (frames the pawn first).

## Suite (not a finish line)
Last full main run PASS 16, FAIL 3, UNMEASURED 25, on a build before the harvest fix and burrow status. Rerun after them: `scorchfruit_produces`, `heat_dome` and `fresh_burn_bonus` pass. `modcheck status` is RED and that partial run cannot clear it. Still failing: `save_holds_no_furnace_herds`, which reads an old dev start save, not this biome; drop it or decide it. Not run: `burn_line`, `embergrass_regrow`.

## Next, in order
1. `python.exe -u Transient/pyre_play/regrow.py` (written, never run; `Transient` is untracked): photographs one real scar to +7 days using only normal speed controls.
2. Look at skies: ash fall, cinderfall. Watch a natural burn reach an ashwallow: does the new status show?
3. Time pods in ordinary play for 2 days (`play.py track`, needs the grant). My one try saw only 2 pods gone, too short to say.
4. With the grant: real base (`jawa/build_batch`), paved strip against a burn, crop on watered vs dry ash, furnace-beast close-up, full suite, census of several fresh maps.
5. Trace the one `Cannot use Graphic_Random.GetColoredVersion with a non-white colorTwo` error in `Player.log`. It came right after a pawn message during a map load or generation.
6. Plan's foils, scenes and showcases are not built. Open `PYRE*` items not re-checked. Firebreak save outcome still not stated.

## Handy
`play.py` verbs added: `track`, `fireshot`, `hour`. A 30,000-tick `safe_advance` can pass the bridge's 240 s limit during burns: use 12,000 or less and `python.exe -u`, and read `action=status` if positions stop changing. Never `pkill -f` a pattern from a shell whose own command contains it.

## Count
- pyre_plant_distribution_correct: true
- pyre_animal_distribution_correct: unseen
- pyre_mapgen_log_clean: unseen
- pyre_ground_deep_ash: true
- pyre_ash_fertile_when_watered: unseen
- pyre_fresh_burn_feeds_the_field: unseen
- pyre_grass_chokes_ground: true
- pyre_embergrass_regrows: unseen
- pyre_burn_line_present: true
- pyre_scorchfruit_fire_born: true
- pyre_scorchfruit_produces: true
- pyre_scorchfruit_spoils_fast: unseen
- pyre_ruins_scorched: true
- pyre_firehawk_carries_ember: unseen
- pyre_furnacebeast_warmth: unseen
- pyre_furnacebeast_heats_room: unseen
- pyre_burrowers_dive: unseen
- pyre_ashfall_darkens_drifts: unseen
- pyre_cinderfall_distinct: unseen
- pyre_blackrain_reads: true
- pyre_cannot_ordinary_rain: true
