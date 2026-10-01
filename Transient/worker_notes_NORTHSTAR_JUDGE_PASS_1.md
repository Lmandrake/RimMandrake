# NORTHSTAR_JUDGE_PASS_1 worker notes

## Status
- started

## Build

## Live pass
- 16:25Z read judge.py, cli.py, bars.py, suite.py, Graffiti validation.py + trial plan §2/§4/§6.
- FINDING: today's 16:12Z live run (agent-aab5 worktree Transient/northstar/Graffiti_20261001T161209Z.json)
  reports 10/10 PASS — suite bars come through `rollup_components`, which never applies the visual
  downgrade `run_bar` applies. So "visual -> UNMEASURED unless judge:" did NOT hold for suite bars.
- FINDING: suite.screenshot's rect path passes no fileName; the tool names files by the SECOND
  (rimbridge_YYYYMMDD_HHMMSS), so same-second shots overwrite. The 16:11Z run has 2 files for the 3
  spree_wall shots (091134, 091135). Gallery chain: 26 files 091136..091202 = 25 gallery shots + beauty.

## Build (done)
- cli.py: results JSON now carries components[] (chain, name, verdict, shows, screenshots[{path,win,wsl}])
  and bar_text {id: {polarity, text}}; suite bars are marked visual and a state PASS reads UNMEASURED
  until judged (state kept in state_status/state_evidence).
- judge_cli.py: parallel 8, 180 s, serial fallback on throttle + one serial retry, cannot-show x3
  unanimity, __cell_rect crop preferred, image checked before asking, model+prompt sha+raw replies kept.
- suite.py: rect screenshots get a unique fileName (same-second overwrite fix).
- selftest_judge.py: 29 checks, mock judge, all pass; auto-discovered by run_selftests.py.
