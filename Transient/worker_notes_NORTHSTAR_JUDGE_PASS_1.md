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
- 16:29Z live pass started: judge_cli.py on Transient/northstar/Graffiti_20261001T161209Z_judged.json (26 reconstructed components, 79 calls, model opus)
- 16:29Z judge running (8 parallel); progress in scratchpad judge_live.log

## Live pass (done) — real `claude -p`, model claude-opus-5-5 (reported), 79 calls, 84 s wall, 0 throttles
- Input: Transient/northstar/Graffiti_20261001T161209Z_judged.json — components RECONSTRUCTED for this
  pre-recording run (chain order x screenshot timestamp order, crop sizes corroborate). Spree shots unmapped.
- Per call: 76 UNJUDGEABLE, 3 NO. Per claim (35): 33 UNMEASURED, 2 FAIL (mark_reads_at_play_zoom on
  gallery_page_1/2: "fragments poking over a wall ... look like debris or rendering glitches").
- Bars: mark_reads_at_play_zoom FAIL; the other 9 UNMEASURED (3 spree bars unjudged; 6 UNJUDGEABLE).
- What the judge saw (and the gallery crop confirms by eye): marks render CLIPPED behind the wall run —
  only slivers above the wall line; one mark is magenta; closeup/dirt crops are 544x75 px strips too
  small to read letters. The judge reported the evidence unfit, it did not pass anything.
- So the 16:12Z run's 10/10 PASS was state-only; the visual half today is 1 FAIL + 9 UNMEASURED.
