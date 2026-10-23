# art_eval run race_r1_incumbent_opus_s2 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ivvol__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 52.3 | opus band REALLY_BAD (model said weak); blocking ['F_TOPDOWN', 'F_NORTH_FACE', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_EARTHLY']; polish ['LEGIB_32'] |
| RM_Ssurr__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 53.1 | opus band REALLY_BAD (model said weak); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'STYLE_CARTOON', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_SIZE_JUMP', 'STYLE_EARTHLY']; polish [] |
| RM_Vizhik__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 47.1 | opus band REALLY_BAD (model said really_bad); blocking ['F_NORTH_FACE', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['F_TOPDOWN', 'STYLE_EARTHLY', 'LEGIB_32'] |
| RM_Sillik__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 32.0 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'STYLE_EARTHLY', 'DESC_MISS', 'DEPARTURE_MISSING', 'F_SOUTH_NOT_FRONT', 'STYLE_CARTOON']; polish ['F_TOPDOWN', 'LEGIB_32'] |
| RM_Dewblade__B | B | plant/ground_cover | WEAK | regen | **REGEN** | 86.0 | opus band WEAK (model said weak); blocking ['DESC_MISS']; polish ['STYLE_EARTHLY', 'SCALE_WRONG', 'WANTS_VARIANTS', 'LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS'] |
| RM_Steamfrond__A | A | plant/bush | WEAK | regen | **REGEN** | 93.6 | opus band WEAK (model said weak); blocking ['ANCHOR', 'LUMP', 'CONSTRUCTED', 'STYLE_CARTOON', 'DESC_MISS']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1', 'K3'], own blocking ['ANCHOR', 'CONSTRUCTED'] |
| Plant_Ambrosia__B | B | plant/bush | REALLY_BAD | - | **REGEN** | 22.4 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO', 'STYLE_OFF']; polish ['WANTS_VARIANTS'] |
| RSW_Convor__A | A | creature/flyer | WEAK | strong_accept | **ACCEPT** | 51.9 | opus band WEAK (model said weak); blocking []; polish ['SCALE_WRONG', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RSW_Rancor__A | A | creature/walker | WEAK | regen | **REGEN** | 57.4 | opus band WEAK (model said weak); blocking ['STYLE_OFF', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['STYLE_OFF', 'F_INCONSISTENT'] |
| RM_Mourvel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 25.3 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY', 'OWNER_NOTE_IGNORED']; polish ['RES_LOW'] |
| RSW_JungleRancor__A | A | creature/walker | WEAK | regen | **REGEN** | 107.5 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'DESC_MISS', 'STYLE_OFF', 'F_SIZE_JUMP']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['DESC_MISS', 'STYLE_OFF', 'ALPHA_HALO'] |
| RSW_KellDragon__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 45.0 | opus band REALLY_BAD (model said weak); blocking ['F_TOPDOWN', 'F_TOPDOWN', 'F_SIZE_JUMP']; polish ['LEGIB_32'] |
| RM_LoomuCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 27.7 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'STYLE_EARTHLY', 'DESC_MISS', 'CATCH_POSE', 'SIBLING_MISMATCH']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
