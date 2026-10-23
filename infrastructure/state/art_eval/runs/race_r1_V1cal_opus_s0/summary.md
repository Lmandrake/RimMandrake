# art_eval run race_r1_V1cal_opus_s0 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Burrak__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 51.0 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_SIZE_JUMP', 'STYLE_OFF']; polish [] |
| RM_Sillik__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 40.5 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['F_TOPDOWN'] |
| RM_Loomu__C | C | creature/swimmer | WEAK | regen | **REGEN** | 111.4 | opus band WEAK (model said really_bad); blocking ['STYLE_CARTOON', 'F_INCONSISTENT', 'F_TOPDOWN', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4'], own blocking ['STYLE_CARTOON', 'F_INCONSISTENT', 'F_SIZE_JUMP'] |
| RM_Gorrask__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 34.9 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'DESC_MISS', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_SIZE_JUMP']; polish ['STYLE_EARTHLY', 'SCALE_WRONG'] |
| RM_Shadefern__B | B | plant/bush | GOOD | - | **ACCEPT** | 23.1 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'STYLE_EARTHLY'] |
| RM_Salvecomb__B | B | plant/bush | GOOD | - | **ACCEPT** | 22.4 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'LEGIB_32'] |
| RM_Weepmat__A | A | plant/ground_cover | WEAK | strong_accept | **ACCEPT** | 42.4 | opus band WEAK (model said good); blocking ['DESC_MISS']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RSW_Mudhorn__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 31.6 | opus band REALLY_BAD (model said good); blocking ['F_SIZE_JUMP', 'X_CROP']; polish [] |
| RSW_Nexu__A | A | creature/walker | WEAK | strong_accept | **ACCEPT** | 62.3 | opus band WEAK (model said good); blocking ['STYLE_CARTOON']; polish ['SCALE_WRONG']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Zhorrel__B | B | plant/tree | WEAK | strong_accept | **ACCEPT** | 40.5 | opus band WEAK (model said good); blocking ['CONSTRUCTED']; polish ['WANTS_VARIANTS']; gpt strong_accept: unsettled [], own blocking [] |
| RSW_MastiffPhalone__A | A | creature/walker | WEAK | regen | **REGEN** | 85.5 | opus band WEAK (model said weak); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'DESC_MISS', 'DESC_MISS']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4'], own blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'DESC_MISS', 'DESC_MISS'] |
| RM_HulduCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 29.9 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE', 'STYLE_EARTHLY']; polish []; unreadable ['SIGNATURE'] |
| RM_LoomuCatch__A | A | creature/catch | REALLY_BAD | - | **REGEN** | 22.6 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'CATCH_WRONG', 'CATCH_POSE', 'DESC_MISS', 'STYLE_EARTHLY', 'STYLE_CARTOON']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V1cal#64d1d9+preamble@v1-V1cal#36a882+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V1cal#f8df95`
