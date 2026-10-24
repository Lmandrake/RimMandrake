# art_eval run fauna_leaningscrub_r3_00

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Chikka | r3 | creature/walker | WEAK | regen | **ESCALATE** | 87.0 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_OFF']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K2'], own blocking ['DESC_MISS']; still failing after 3 regen rounds — one line to the owner |
| RM_Crustweevil | r3 | creature/walker | WEAK | regen | **ESCALATE** | 80.7 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'ALPHA_HALO']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'ALPHA_HALO']; still failing after 3 regen rounds — one line to the owner |
| RM_Durrok | r3 | creature/walker | WEAK | regen | **ESCALATE** | 87.8 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Chikka: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Crustweevil: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Durrok: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
