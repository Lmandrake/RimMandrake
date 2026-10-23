# art_eval run race_r1_V1cal_opus_s2 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ivvol__C | C | creature/swimmer | WEAK | regen | **REGEN** | 112.2 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_TOPDOWN', 'F_SIZE_JUMP'] |
| RM_Ssurr__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 43.7 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish [] |
| RM_Vizhik__C | C | creature/swimmer | WEAK | regen | **REGEN** | 114.0 | opus band WEAK (model said really_bad); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['LEGIB_32', 'F_TOPDOWN']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING'] |
| RM_Sillik__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 33.4 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'STYLE_EARTHLY', 'DESC_MISS', 'DEPARTURE_MISSING', 'F_SOUTH_NOT_FRONT', 'STYLE_CARTOON']; polish ['F_TOPDOWN', 'LEGIB_32'] |
| RM_Dewblade__B | B | plant/ground_cover | WEAK | strong_accept | **ACCEPT** | 80.4 | opus band WEAK (model said weak); blocking ['DESC_MISS']; polish ['STYLE_EARTHLY', 'SCALE_WRONG', 'WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Steamfrond__A | A | plant/bush | WEAK | strong_accept | **ACCEPT** | 71.9 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'ANCHOR', 'CONSTRUCTED', 'LUMP', 'STYLE_CARTOON', 'DESC_MISS']; polish ['WANTS_VARIANTS']; gpt strong_accept: unsettled [], own blocking [] |
| Plant_Ambrosia__B | B | plant/bush | WEAK | regen | **REGEN** | 49.9 | opus band WEAK (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DESC_MISS', 'ALPHA_HALO'] |
| RSW_Convor__A | A | creature/flyer | GOOD | - | **ACCEPT** | 27.1 | opus band GOOD (model said good); blocking []; polish ['SCALE_WRONG'] |
| RSW_Rancor__A | A | creature/walker | WEAK | regen | **REGEN** | 62.9 | opus band WEAK (model said good); blocking ['STYLE_OFF']; polish []; gpt regen: unsettled ['K1'], own blocking ['STYLE_OFF'] |
| RM_Mourvel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 27.3 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY']; polish [] |
| RSW_JungleRancor__A | A | creature/walker | WEAK | regen | **REGEN** | 91.7 | opus band WEAK (model said good); blocking ['DESC_MISS', 'F_INCONSISTENT', 'STYLE_OFF', 'ALPHA_HALO']; polish []; gpt regen: unsettled ['K1', 'K3', 'K4'], own blocking ['DESC_MISS', 'STYLE_OFF', 'ALPHA_HALO'] |
| RSW_KellDragon__B | B | creature/walker | WEAK | regen | **REGEN** | 73.8 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_TOPDOWN'] |
| RM_LoomuCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 24.7 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'STYLE_EARTHLY', 'DESC_MISS', 'CATCH_POSE']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V1cal#64d1d9+preamble@v1-V1cal#36a882+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V1cal#f8df95`
