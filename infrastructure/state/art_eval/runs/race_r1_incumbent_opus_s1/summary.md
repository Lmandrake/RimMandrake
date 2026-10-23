# art_eval run race_r1_incumbent_opus_s1 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Gorrask__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 51.3 | opus band REALLY_BAD (model said weak); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'STYLE_OFF']; polish [] |
| RM_Huldu__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 39.9 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'F_TOPDOWN', 'STYLE_CARTOON', 'F_SIZE_JUMP']; polish ['LEGIB_32'] |
| RM_Murrin__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 52.4 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_INCONSISTENT', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_NORTH_FACE']; polish ['STYLE_EARTHLY', 'LEGIB_32'] |
| RM_Burrak__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 38.2 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'DEPARTURE_MISSING', 'DESC_MISS', 'STYLE_EARTHLY', 'F_TOPDOWN', 'F_SOUTH_NOT_FRONT', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'STYLE_CARTOON']; polish ['SCALE_WRONG'] |
| RM_Bladderquill__B | B | plant/bush | WEAK | strong_accept | **ACCEPT** | 58.1 | opus band WEAK (model said weak); blocking ['STYLE_EARTHLY']; polish ['SCALE_WRONG', 'WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Rockfinger__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 29.4 | opus band REALLY_BAD (model said weak); blocking ['STYLE_EARTHLY', 'ANCHOR']; polish ['SCALE_WRONG', 'WANTS_VARIANTS'] |
| RM_Dripfringe__B | B | plant/special | WEAK | regen | **REGEN** | 54.3 | opus band WEAK (model said weak); blocking ['ANCHOR', 'STYLE_EARTHLY']; polish ['LEGIB_32', 'WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['ANCHOR'] |
| RM_Fuzzviper__B | B | creature/walker | WEAK | regen | **REGEN** | 75.5 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'STYLE_EARTHLY']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_TOPDOWN'] |
| RSW_Anooba__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 31.6 | opus band REALLY_BAD (model said weak); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'F_SIZE_JUMP']; polish [] |
| RM_Ghemmel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 28.8 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY', 'STYLE_CARTOON']; polish ['LEGIB_32', 'WANTS_VARIANTS'] |
| RSW_Insectomorph__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 40.8 | opus band REALLY_BAD (model said really_bad); blocking ['F_NORTH_FACE', 'DUPLICATE', 'F_TOPDOWN', 'F_INCONSISTENT', 'DESC_MISS']; polish ['LEGIB_32'] |
| RSW_Gualaar__A | A | creature/walker | WEAK | regen | **REGEN** | 90.0 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'STYLE_OFF']; polish ['STYLE_EARTHLY']; gpt regen: unsettled ['K2'], own blocking ['STYLE_OFF'] |
| RM_IvvolCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 22.5 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'STYLE_EARTHLY']; polish ['LEGIB_32'] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
