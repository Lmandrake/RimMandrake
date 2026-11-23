# Pyrelands 0.1.0: in-game acceptance, visit 7 (Archmagi, ArchSmall)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_SEVEN. Started 2026-11-23 05:01 PST.

## Progress

- 05:10 skeleton written; item claimed; ArchSmall free and running, ArchBig held by another BENCH run (not ours).

- 05:26 the `pyrelands` tier now holds 18 mods (Huge Things joined it since visit 6): HugeThings deployed to ArchSmall (DLL drift), tier applied (`evidence/modset_pyrelands.log`, live list backed up to `evidence/ModsConfig.ArchSmall.before_visit7.xml`), ArchSmall relaunched (pid 48136). Compose biomes in sync (Ullai art already deployed); companion source unchanged since its deployed 3a0b257fcf52, not rebuilt. Gate A: every row PASS (def fp 417df172fdb5e402) but 3.8.12 loadavg 14.3 (other agents' selftests and git on this machine; not this run's to lower). A fresh site built on the 18-mod list: tile 193, 51.7 C, `NS_Pyrelands_site_1_417df172fdb5_visit7`; gate B CLEAN. Main batch of 33 items started (`scripts/runner.sh`, `evidence/runner.log`). SteveDesktop not used: visits 2 and 5 measured no Pyrelands site there.
- 05:36 16 of 33 main items done, all PASS but P_furnace_room: furnacebeast_heats_room FAIL, beast room +0.3 C over the control (needs +10). Both rooms read openRoofCount 25 after the series (visit 6: 0). Theory: Huge Things, a hard dependency of the composed biomes since 0dc82e3270 (2026-11-23 00:25) and so new on this tier, rates the furnace-beast (body size 9) tier T2 (>= 8), and a T2 pawn's wake holes every thin roof cell it enters (TitanicWakeProcessor.ProcessRoof): the beast unroofs its own pen. Experiment queued after the batch: the same chain with Huge Things' wakeRoofHolingEnabled off (`scripts/hugethings_roof.py`), and a roof probe with no beast (`scripts/roof_probe.py`).
- 06:05 sc_flamefang_venom read 4 rows UNMEASURED: the biter (declared a fixture) arrived and bit in one 60-tick sub-step, and clockgate refused the stop because a 'hurt' rode along, a kind BITE_STOP_ON leaves out on purpose (HARNESS; visit 6 passed on timing). Filed and fixed RIMMANDRAKE_RESUME_FIXTURE_ARRIVAL_PAST_UNASKED_BITE (5e888e1af2, selftest_clockgate 85/86 on the parent, 86/86 now); venom rerun and its planted wrong-tend run queued. 28 of 35 rows PASS so far; burn_line running.
- 06:30 burn_line 4/4 PASS on its numbers (25 min). Its whole-map day-end captures are real for the first time (visit 6's were desktop grabs) and show the mod's fire leaving thin one-cell horizontal lanes across the map, long straight-edged burned bands and a ruler-straight front (`screenshots/burn_line_dayend_sheet.jpg`, `screenshots/burn_line_hourly_sheet.jpg`): what RIMMANDRAKE_WIDEN_PYRE_FIRE_TRAILS_RUN_AS_RULER_STRAIGHT_LANES fixed in its offline model. A live read of that model's own strand-share proxy queued (`scripts/lanes_probe.py` on the burn_line_walking save).
- 07:22 ash_fertility_watered PASS. fresh_burn_bonus: fresh_burn_feeds_the_field PASS, burn_compounds_with_black_rain UNMEASURED: the 'old ash' control pad C carried a fresh-burn stamp at tick 413443, set during the first row's day-1 wait (384001 to 444001), 40 cells from that row's firebreaked burn, with burn line, fire-hawk spread and fire clock isolated. Cause not yet read (SITE presumed: a fire from elsewhere on the map reached the control pad). Rerun queued with a map-wide burn-stamp read after it. The regrow chain running since 06:55.
- 07:31 the main runner was killed at its 2-hour background limit during scorchfruit_spoils (requeued); every other main chain had finished. Follow batch (`runner.log`, START follow 07:31:53): P_furnace_room experiment: Huge Things' wakeRoofHolingEnabled off -> PASS (beast room 79.0 C, +24.8, 0 open roof cells); back on -> FAIL twice (+0.3 C, 25 open); no beast -> roofs stay (script_roof_probe.log). Class MOD, unfixed (design choice), filed RIMMANDRAKE_SPARE_PYRE_FURNACE_BARN_ROOF_FROM_TITAN_WAKE.
- 07:42 sc_flamefang_venom on the repaired clockgate (5e888e1af2): 5/5 PASS (flamefang_venom2); planted wrong tend -> venom_tended_vs_untended FAIL. HARNESS repair shown both ways.
- 07:50 lane read of the burn_line_walking save: strand share 0.056 (limit 0.25) PASS, no one-cell run of 20 cells along x; but its burn map (`evidence/lanes_burn_line_walking_mask.png`) shows straight one-cell burned trails away from the front, about 20-26 cells each. What moves along them: `scripts/line_speed.py` queued.

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: (not yet written)
exit_met: false
```
