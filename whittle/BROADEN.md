# Different-model consultation

Question: `whittle/broaden-question.txt` contains the frozen statement, implemented mechanisms, tested math controls and authored live scenarios, asking what real players would do that these miss.

Command: `WHITTLE=0 claude --model opus --effort high --max-budget-usd 5 --tools '' -p "$(cat whittle/broaden-question.txt)"`.

Raw answer: `whittle/broaden-second-raw.txt`. The initial attempt (`whittle/broaden-raw.txt`) failed because its child inherited WHITTLE=1; the installed stop hook demanded files from a text-only consultation. Observer identified this harness fault. Its output and STALLED record are preserved, not counted as a consultation.

Opus identified the transition to an upright prisoner and serialization while occupied as revealing gaps. Acted on both in `scene_hole_prison`: ordinary DeliverFood and actual self-ingestion after the prisoner stands (a separately labelled fixture heal if natural recovery has not occurred), and an occupied save/reload followed by held/bed-transfer checks. The prior scene-begin snapshot remains the final restore target.

Results: `whittle/evidence/offline-tests-stable.log` reports PASS 2/2 selected test files; the new driver test exercises both successful occupied reload and loss of prison status, plus capture/feed/escape and restoration failures, then compiles/runs only PitRoom_* C# cases. The two added cases remain LIVE UNMEASURED: required preflight O10/O13 prevents launch. No fake-bridge outcome is offered as proof of game behavior. The occupied-save and awake-feeding probes are authored, not claimed exercised in a game.
