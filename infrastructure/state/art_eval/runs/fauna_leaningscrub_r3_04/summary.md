# art_eval run fauna_leaningscrub_r3_04

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_TunnelSnake | r3 | creature/walker | REALLY_BAD | - | **ESCALATE** | 31.8 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'F_NORTH_FACE']; polish ['F_TOPDOWN', 'LEGIB_32']; still failing after 3 regen rounds — one line to the owner |
| RM_Vissler | r3 | creature/walker | WEAK | regen | **ESCALATE** | 76.1 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_CARTOON']; polish ['MATERIAL_PAINT']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT']; still failing after 3 regen rounds — one line to the owner |
| RM_Vurra | r3 | creature/walker | WEAK | regen | **ESCALATE** | 78.4 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP']; polish ['F_TOPDOWN']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_TunnelSnake: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Vissler: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Vurra: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
