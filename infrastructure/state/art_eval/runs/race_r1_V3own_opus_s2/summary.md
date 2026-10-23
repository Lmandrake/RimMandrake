# art_eval run race_r1_V3own_opus_s2 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ivvol__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 51.3 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['LEGIB_32'] |
| RM_Ssurr__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 44.3 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'STYLE_CARTOON', 'DEPARTURE_MISSING']; polish [] |
| RM_Vizhik__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 48.1 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_NORTH_FACE']; polish ['F_TOPDOWN', 'LEGIB_32'] |
| RM_Sillik__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 38.5 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_SOUTH_NOT_FRONT', 'STYLE_CARTOON', 'F_SIZE_JUMP']; polish ['F_TOPDOWN', 'LEGIB_32'] |
| RM_Dewblade__B | B | plant/ground_cover | WEAK | regen | **REGEN** | 62.0 | opus band WEAK (model said really_bad); blocking ['DESC_MISS', 'ANCHOR']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS', 'SCALE_WRONG']; gpt regen: unsettled ['K1', 'K2'], own blocking ['ANCHOR'] |
| RM_Steamfrond__A | A | plant/bush | WEAK | strong_accept | **ACCEPT** | 68.9 | opus band WEAK (model said really_bad); blocking ['LUMP', 'ANCHOR', 'CONSTRUCTED', 'STYLE_CARTOON']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| Plant_Ambrosia__B | B | plant/bush | REALLY_BAD | - | **REGEN** | 26.3 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO', 'STYLE_CARTOON']; polish ['WANTS_VARIANTS'] |
| RSW_Convor__A | A | creature/flyer | GOOD | - | **ACCEPT** | 29.0 | opus band GOOD (model said good); blocking []; polish ['SCALE_WRONG'] |
| RSW_Rancor__A | A | creature/walker | WEAK | regen | **REGEN** | 53.8 | opus band WEAK (model said good); blocking ['STYLE_OFF']; polish []; gpt regen: unsettled ['K1'], own blocking ['STYLE_OFF'] |
| RM_Mourvel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 23.3 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY']; polish ['WANTS_VARIANTS'] |
| RSW_JungleRancor__A | A | creature/walker | WEAK | regen | **REGEN** | 85.8 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'CANON_MISS', 'DESC_MISS', 'STYLE_OFF']; polish []; gpt regen: unsettled ['K2', 'K3', 'K4'], own blocking ['DESC_MISS', 'STYLE_OFF', 'ALPHA_HALO'] |
| RSW_KellDragon__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 42.6 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'F_TOPDOWN']; polish [] |
| RM_LoomuCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 23.7 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'STYLE_EARTHLY', 'DESC_MISS', 'CATCH_POSE']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V3own#33f5d7+preamble@v1-V3own#b2a1a8+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
