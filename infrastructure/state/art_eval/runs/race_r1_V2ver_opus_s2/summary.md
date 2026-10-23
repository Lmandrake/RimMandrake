# art_eval run race_r1_V2ver_opus_s2 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ivvol__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 65.8 | opus band REALLY_BAD (model said weak); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish [] |
| RM_Ssurr__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 63.0 | opus band REALLY_BAD (model said weak); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['LEGIB_32', 'SCALE_WRONG'] |
| RM_Vizhik__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 50.2 | opus band REALLY_BAD (model said weak); blocking ['F_NORTH_FACE', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DESC_MISS', 'STYLE_CARTOON']; polish ['F_TOPDOWN', 'LEGIB_32'] |
| RM_Sillik__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 39.5 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'F_SOUTH_NOT_FRONT', 'DESC_MISS', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['F_TOPDOWN'] |
| RM_Dewblade__B | B | plant/ground_cover | WEAK | regen | **REGEN** | 73.8 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'ANCHOR']; polish ['STYLE_EARTHLY', 'LEGIB_32', 'WANTS_VARIANTS']; gpt regen: unsettled ['K1', 'K2'], own blocking ['ANCHOR'] |
| RM_Steamfrond__A | A | plant/bush | WEAK | regen | **REGEN** | 88.0 | opus band WEAK (model said weak); blocking ['ANCHOR', 'LUMP', 'STYLE_CARTOON', 'DESC_MISS', 'CONSTRUCTED']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['ANCHOR'] |
| Plant_Ambrosia__B | B | plant/bush | REALLY_BAD | - | **REGEN** | 32.8 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO', 'STYLE_CARTOON']; polish ['WANTS_VARIANTS'] |
| RSW_Convor__A | A | creature/flyer | GOOD | - | **ACCEPT** | 42.2 | opus band GOOD (model said good); blocking []; polish ['SCALE_WRONG'] |
| RSW_Rancor__A | A | creature/walker | WEAK | regen | **REGEN** | 72.5 | opus band WEAK (model said good); blocking ['STYLE_OFF', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['STYLE_OFF', 'F_INCONSISTENT'] |
| RM_Mourvel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 29.3 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY']; polish ['SCALE_WRONG'] |
| RSW_JungleRancor__A | A | creature/walker | WEAK | regen | **REGEN** | 116.7 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'DESC_MISS', 'F_SIZE_JUMP', 'STYLE_OFF']; polish []; gpt regen: unsettled ['K1', 'K2', 'K4'], own blocking ['DESC_MISS', 'DESC_MISS', 'STYLE_OFF', 'ALPHA_HALO'] |
| RSW_KellDragon__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 45.6 | opus band REALLY_BAD (model said weak); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'F_INCONSISTENT']; polish [] |
| RM_LoomuCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 36.4 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'STYLE_EARTHLY', 'DESC_MISS', 'CATCH_POSE', 'SIBLING_MISMATCH']; polish ['SCALE_WRONG'] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V2ver#1d5b9e+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V2ver#853bd2`
