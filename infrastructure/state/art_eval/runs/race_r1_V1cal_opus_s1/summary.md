# art_eval run race_r1_V1cal_opus_s1 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Gorrask__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 50.5 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'DEPARTURE_MISSING']; polish [] |
| RM_Huldu__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 40.4 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_TOPDOWN', 'F_INCONSISTENT', 'DESC_MISS']; polish ['SCALE_WRONG'] |
| RM_Murrin__C | C | creature/swimmer | WEAK | regen | **REGEN** | 112.8 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'ALPHA_HALO', 'STYLE_CARTOON']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'ALPHA_HALO'] |
| RM_Burrak__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 36.3 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'DESC_MISS', 'DEPARTURE_MISSING', 'STYLE_EARTHLY', 'F_TOPDOWN', 'F_SOUTH_NOT_FRONT', 'STYLE_CARTOON', 'F_SIZE_JUMP']; polish ['SCALE_WRONG'] |
| RM_Bladderquill__B | B | plant/bush | WEAK | strong_accept | **ACCEPT** | 58.0 | opus band WEAK (model said good); blocking ['STYLE_EARTHLY']; polish ['SCALE_WRONG', 'WANTS_VARIANTS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Rockfinger__B | B | plant/tree | WEAK | regen | **REGEN** | 50.9 | opus band WEAK (model said good); blocking ['STYLE_EARTHLY']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['STYLE_EARTHLY'] |
| RM_Dripfringe__B | B | plant/special | WEAK | strong_accept | **ACCEPT** | 47.2 | opus band WEAK (model said good); blocking ['ANCHOR']; polish ['WANTS_VARIANTS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Fuzzviper__B | B | creature/walker | WEAK | regen | **REGEN** | 65.0 | opus band WEAK (model said good); blocking ['F_TOPDOWN']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_TOPDOWN'] |
| RSW_Anooba__B | B | creature/walker | WEAK | strong_accept | **ACCEPT** | 71.2 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Ghemmel__B | B | plant/tree | WEAK | regen | **REGEN** | 66.4 | opus band WEAK (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS'] |
| RSW_Insectomorph__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 32.7 | opus band REALLY_BAD (model said really_bad); blocking ['F_NORTH_FACE', 'F_INCONSISTENT', 'DUPLICATE', 'DESC_MISS']; polish [] |
| RSW_Gualaar__A | A | creature/walker | WEAK | strong_accept | **ACCEPT** | 51.6 | opus band WEAK (model said good); blocking ['STYLE_OFF']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_IvvolCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 24.4 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'DESC_MISS', 'STYLE_EARTHLY']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V1cal#64d1d9+preamble@v1-V1cal#36a882+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V1cal#f8df95`
