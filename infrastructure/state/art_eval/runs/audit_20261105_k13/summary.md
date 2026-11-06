# art_eval run audit_20261105_k13

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_Scavrat | r1 | creature/walker | GOOD | - | **ACCEPT** | 33.5 | opus band GOOD (model said good); blocking []; polish ['SCALE_WRONG', 'LEGIB_32']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RSW_ShiroTrap__ShiroTrap_i | r1 | creature/walker | WEAK | regen | **REGEN** | 71.4 | opus band WEAK (model said good); blocking ['STYLE_EARTHLY']; polish []; gpt regen: unsettled ['K1'], own blocking ['STYLE_EARTHLY']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RSW_Torton__Torton_f | r1 | creature/walker | WEAK | - | **HOLD_ERROR** | 57.8 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_OFF']; polish []; gpt: eval pipeline: a WEAK Opus pass goes to the GPT targeted second look (owner 2026-10-23)
[consult] 16783 chars, 0 file(s), 5 image(s), model gpt-6.1-sol, round -, job D:\ClaudeWork\rimmandrake\scratch\codex\consult-20261105-193720-823835-d9661e
[consult] receipt job consult-20261105-193720-823835-d9661e
ERRO |
| RSW_TunnelSnake | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.3 | canvas not the shipping rule for drawSize [2.7, 2.7]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512 |

## One line each for the owner
- RSW_Torton__Torton_f: HOLD_ERROR — gpt: eval pipeline: a WEAK Opus pass goes to the GPT targeted second look (owner 2026-10-23)
[consult] 16783 chars, 0 file(s), 5 image(s), model gpt-6.1-sol, round -, job D:\ClaudeWork\rimmandrake\scratch\codex\consult-20261105-193720-823835-d9661e
[consult] receipt job consult-20261105-193720-823835-d9661e
ERROR: no answer (exit 1 after 10s). Job kept: /mnt/d/ClaudeWork/rimmandrake/scratch/codex/consult-20261105-193720-823835-d9661e
<3>WSL (823845 - ) ERROR: UtilAcceptVsock:273: accept4 failed 110


- RSW_TunnelSnake: HOLD_CANVAS — canvas not the shipping rule for drawSize [2.7, 2.7]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512

Models reported: UNMEASURED, claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
