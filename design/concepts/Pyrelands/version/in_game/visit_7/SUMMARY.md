# Pyrelands 0.1.0: in-game acceptance, visit 7 (Archmagi, ArchSmall)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_SEVEN. Started 2026-11-23 05:01 PST.

## Progress

- 05:10 skeleton written; item claimed; ArchSmall free and running, ArchBig held by another BENCH run (not ours).

- 05:26 the `pyrelands` tier now holds 18 mods (Huge Things joined it since visit 6): HugeThings deployed to ArchSmall (DLL drift), tier applied (`evidence/modset_pyrelands.log`, live list backed up to `evidence/ModsConfig.ArchSmall.before_visit7.xml`), ArchSmall relaunched (pid 48136). Compose biomes in sync (Ullai art already deployed); companion source unchanged since its deployed 3a0b257fcf52, not rebuilt. Gate A: every row PASS (def fp 417df172fdb5e402) but 3.8.12 loadavg 14.3 (other agents' selftests and git on this machine; not this run's to lower). A fresh site built on the 18-mod list: tile 193, 51.7 C, `NS_Pyrelands_site_1_417df172fdb5_visit7`; gate B CLEAN. Main batch of 33 items started (`scripts/runner.sh`, `evidence/runner.log`). SteveDesktop not used: visits 2 and 5 measured no Pyrelands site there.
- 05:36 16 of 33 main items done, all PASS but P_furnace_room: furnacebeast_heats_room FAIL, beast room +0.3 C over the control (needs +10). Both rooms read openRoofCount 25 after the series (visit 6: 0). Theory: Huge Things, a hard dependency of the composed biomes since 0dc82e3270 (2026-11-23 00:25) and so new on this tier, rates the furnace-beast (body size 9) tier T2 (>= 8), and a T2 pawn's wake holes every thin roof cell it enters (TitanicWakeProcessor.ProcessRoof): the beast unroofs its own pen. Experiment queued after the batch: the same chain with Huge Things' wakeRoofHolingEnabled off (`scripts/hugethings_roof.py`), and a roof probe with no beast (`scripts/roof_probe.py`).

## Exit

```
ingame_rows: {}
strange_open: 0
savegame: (not yet written)
exit_met: false
```
