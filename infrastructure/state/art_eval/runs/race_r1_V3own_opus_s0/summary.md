# art_eval run race_r1_V3own_opus_s0 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Burrak__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 42.7 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'F_INCONSISTENT', 'F_TOPDOWN', 'DEPARTURE_MISSING', 'F_SIZE_JUMP']; polish [] |
| RM_Sillik__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 45.4 | opus band REALLY_BAD (model said really_bad); blocking ['F_SOUTH_NOT_FRONT', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['F_TOPDOWN', 'LEGIB_32'] |
| RM_Loomu__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 37.3 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'STYLE_CARTOON', 'DEPARTURE_MISSING']; polish ['LEGIB_32'] |
| RM_Gorrask__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 31.3 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'DESC_MISS', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['STYLE_EARTHLY', 'SCALE_WRONG'] |
| RM_Shadefern__B | B | plant/bush | GOOD | - | **ACCEPT** | 22.5 | opus band GOOD (model said good); blocking []; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS', 'LEGIB_32'] |
| RM_Salvecomb__B | B | plant/bush | WEAK | strong_accept | **ACCEPT** | 42.3 | opus band WEAK (model said good); blocking ['STYLE_EARTHLY']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Weepmat__A | A | plant/ground_cover | WEAK | regen | **REGEN** | 48.7 | opus band WEAK (model said good); blocking ['DESC_MISS']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS'] |
| RSW_Mudhorn__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 37.9 | opus band REALLY_BAD (model said good); blocking ['F_SIZE_JUMP', 'X_CROP']; polish ['MATERIAL_PAINT'] |
| RSW_Nexu__A | A | creature/walker | WEAK | regen | **REGEN** | 96.5 | opus band WEAK (model said good); blocking ['STYLE_CARTOON', 'F_SIZE_JUMP']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K2'], own blocking ['F_SIZE_JUMP'] |
| RM_Zhorrel__B | B | plant/tree | WEAK | regen | **REGEN** | 49.0 | opus band WEAK (model said good); blocking ['DESC_MISS']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS'] |
| RSW_MastiffPhalone__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 33.5 | opus band REALLY_BAD (model said good); blocking ['DESC_MISS', 'DESC_MISS', 'DESC_MISS', 'F_SIZE_JUMP']; polish [] |
| RM_HulduCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 24.4 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE', 'STYLE_EARTHLY']; polish ['LEGIB_32'] |
| RM_LoomuCatch__A | A | creature/catch | REALLY_BAD | - | **REGEN** | 29.3 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'CATCH_WRONG', 'CATCH_POSE', 'STYLE_EARTHLY', 'STYLE_CARTOON', 'DESC_MISS']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V3own#33f5d7+preamble@v1-V3own#b2a1a8+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
