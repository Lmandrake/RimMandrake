# art_eval run e2e_weepingstones_20261023 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ssurr | B | creature/walker | REALLY_BAD | - | **REGEN** | 58.1 | opus band REALLY_BAD (model said weak); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'STYLE_CARTOON', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32'] |
| RM_Huldu | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 52.1 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'F_TOPDOWN', 'F_SIZE_JUMP', 'STYLE_CARTOON']; polish ['LEGIB_32'] |
| RM_Vellak | B | creature/pack | WEAK | regen | **REGEN** | 99.2 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'STYLE_EARTHLY', 'STYLE_CARTOON', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RM_Burrak | B | creature/walker | REALLY_BAD | - | **REGEN** | 61.0 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'F_INCONSISTENT', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'F_SIZE_JUMP', 'STYLE_OFF']; polish [] |
| RM_Shadefern | B | plant/bush | WEAK | regen | **REGEN** | 57.0 | opus band WEAK (model said weak); blocking ['STYLE_EARTHLY', 'STYLE_OFF']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['STYLE_EARTHLY'] |
| RM_HulduCatch | C | creature/catch | - | - | **REGEN_AFTER_SOURCE** | 0.1 | living RM_Huldu decision REGEN |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v1#946be1+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v2#1b8dfa+creature@v2#16a385`
