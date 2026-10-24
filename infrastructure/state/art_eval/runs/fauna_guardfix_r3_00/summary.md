# art_eval run fauna_guardfix_r3_00

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Zisska | r3 | creature/walker | WEAK | strong_accept | **ACCEPT** | 94.6 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'F_SOUTH_NOT_FRONT']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Surrik | r3 | creature/walker | REALLY_BAD | - | **ESCALATE** | 39.4 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; still failing after 3 regen rounds — one line to the owner |
| RM_SparkleechGrub | r3 | creature/walker | WEAK | strong_accept | **ACCEPT** | 140.1 | opus band WEAK (model said really_bad); blocking ['F_SOUTH_NOT_FRONT', 'F_NORTH_FACE', 'ALPHA_HALO']; polish ['F_TOPDOWN', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |

## One line each for the owner
- RM_Surrik: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
