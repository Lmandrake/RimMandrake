# art_eval run audit_20261105_h2

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_SandLeaper_n | r3 | creature/walker | WEAK | regen | **ESCALATE** | 88.6 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING', 'F_TOPDOWN']; polish []; gpt regen: unsettled ['K1', 'K3'], own blocking ['F_INCONSISTENT']; still failing after 3 regen rounds — one line to the owner |
| RSW_Varactyl__Varactyl_f_n | r3 | creature/walker | WEAK | strong_accept | **ACCEPT** | 61.6 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'CANON_MISS']; polish []; gpt strong_accept: unsettled [], own blocking []; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_Drazzik_n | r3 | creature/walker | WEAK | strong_accept | **ACCEPT** | 93.1 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP']; polish []; gpt strong_accept: unsettled [], own blocking []; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |

## One line each for the owner
- RSW_SandLeaper_n: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
