# art_eval run fauna_leaningscrub_r3_02

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ribbonwhip | r3 | creature/walker | WEAK | regen | **ESCALATE** | 109.7 | opus band WEAK (model said really_bad); blocking ['ALPHA_HALO', 'DESC_MISS', 'F_SOUTH_NOT_FRONT', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K3', 'K4'], own blocking ['ALPHA_HALO', 'F_SOUTH_NOT_FRONT']; still failing after 3 regen rounds — one line to the owner |
| RM_Rollbug | r3 | creature/walker | WEAK | regen | **ESCALATE** | 67.0 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT']; still failing after 3 regen rounds — one line to the owner |
| RM_Shirrel | r3 | creature/walker | REALLY_BAD | - | **ESCALATE** | 40.7 | opus band REALLY_BAD (model said really_bad); blocking ['DEPARTURE_MISSING', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT']; polish ['FLYER_WINGS_GROUNDED']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Ribbonwhip: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Rollbug: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Shirrel: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
