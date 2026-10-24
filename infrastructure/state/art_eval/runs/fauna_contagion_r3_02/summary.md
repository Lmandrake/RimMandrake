# art_eval run fauna_contagion_r3_02

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Meltgut | r3 | creature/walker | WEAK | regen | **ESCALATE** | 126.0 | opus band WEAK (model said weak); blocking ['F_SOUTH_NOT_FRONT', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish ['F_TOPDOWN', 'SCALE_WRONG']; gpt regen: unsettled ['K2', 'K3', 'K4'], own blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; still failing after 3 regen rounds — one line to the owner |
| RM_OcularJelly | r3 | creature/walker | WEAK | regen | **ESCALATE** | 60.0 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING']; still failing after 3 regen rounds — one line to the owner |
| RM_Peeper | r3 | creature/walker | REALLY_BAD | - | **ESCALATE** | 28.3 | opus band REALLY_BAD (model said really_bad); blocking ['F_SOUTH_NOT_FRONT', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'X_WRONG']; polish []; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Meltgut: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_OcularJelly: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Peeper: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
