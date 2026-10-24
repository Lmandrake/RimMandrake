# art_eval run fauna_leaningscrub_r3_03

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Shokka | r3 | creature/walker | REALLY_BAD | - | **ESCALATE** | 36.0 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'F_INCONSISTENT', 'STYLE_EARTHLY']; polish []; still failing after 3 regen rounds — one line to the owner |
| RM_Thornhold | r3 | creature/walker | WEAK | strong_accept | **ACCEPT** | 82.0 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Tikkit | r3 | creature/walker | WEAK | strong_accept | **ACCEPT** | 76.9 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |

## One line each for the owner
- RM_Shokka: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
