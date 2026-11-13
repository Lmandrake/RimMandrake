tick:raised SystemExit 143 is the metronome killing the Dispatcher tick at its dispatch-phase limit (~20 s): /mnt/d/ClaudeWork/rimmandrake/metronome/shadow/beats.jsonl rows phase=dispatch exit=overrun killed=killed_term. 2026-11-13: 20 kills 18:13-20:37Z, none after, but the slowest clean beat since is 18.4 s, so headroom is 1.6 s. Read beats.jsonl before the Dispatcher journal when a tick raises; rm-dispatcher.timer is inactive because the metronome owns the clock.
item: NONE
home: NONE
