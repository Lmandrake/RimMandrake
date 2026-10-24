# art_eval run fauna_leaningscrub_r3_01

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Dustflutter | r3 | creature/flyer | WEAK | regen | **ESCALATE** | 76.1 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32', 'SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING']; still failing after 3 regen rounds — one line to the owner |
| RM_Fuzzrunner | r3 | creature/walker | WEAK | regen | **ESCALATE** | 75.6 | opus band WEAK (model said weak); blocking ['STYLE_EARTHLY', 'STYLE_CARTOON', 'F_INCONSISTENT', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K3', 'K4'], own blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING']; still failing after 3 regen rounds — one line to the owner |
| RM_Fuzzviper | r3 | creature/walker | WEAK | regen | **ESCALATE** | 66.4 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING']; polish ['LEGIB_32', 'SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Dustflutter: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Fuzzrunner: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Fuzzviper: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
