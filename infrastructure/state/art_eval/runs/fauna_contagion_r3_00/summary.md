# art_eval run fauna_contagion_r3_00

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Bloodlurk | r3 | creature/walker | WEAK | regen | **ESCALATE** | 85.5 | opus band WEAK (model said really_bad); blocking ['F_NORTH_FACE', 'F_INCONSISTENT', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K3'], own blocking ['F_NORTH_FACE', 'DEPARTURE_MISSING']; still failing after 3 regen rounds — one line to the owner |
| RM_ContagionIkee | r3 | creature/walker | WEAK | regen | **ESCALATE** | 57.6 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT']; still failing after 3 regen rounds — one line to the owner |
| RM_Danglemaw | r3 | creature/walker | WEAK | regen | **ESCALATE** | 65.8 | opus band WEAK (model said weak); blocking ['F_NORTH_FACE', 'DUPLICATE', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_NORTH_FACE']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Bloodlurk: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_ContagionIkee: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Danglemaw: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
