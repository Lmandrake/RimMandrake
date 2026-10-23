# art_eval run race_r1_V2ver_opus_s1 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Gorrask__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 58.6 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish [] |
| RM_Huldu__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 43.4 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_TOPDOWN', 'F_INCONSISTENT', 'STYLE_CARTOON', 'F_SIZE_JUMP', 'F_NORTH_FACE']; polish ['LEGIB_32']; unreadable ['SAME_SIZE'] |
| RM_Murrin__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 60.4 | opus band REALLY_BAD (model said weak); blocking ['F_TOPDOWN', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'STYLE_CARTOON', 'ALPHA_HALO']; polish ['STYLE_EARTHLY', 'LEGIB_32', 'SCALE_WRONG'] |
| RM_Burrak__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 44.8 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'DESC_MISS', 'DEPARTURE_MISSING', 'F_TOPDOWN', 'F_SOUTH_NOT_FRONT', 'STYLE_CARTOON', 'STYLE_EARTHLY', 'F_INCONSISTENT', 'F_SIZE_JUMP']; polish ['SCALE_WRONG'] |
| RM_Bladderquill__B | B | plant/bush | WEAK | strong_accept | **ACCEPT** | 76.9 | opus band WEAK (model said weak); blocking ['STYLE_EARTHLY', 'STYLE_CARTOON']; polish ['SCALE_WRONG', 'WANTS_VARIANTS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Rockfinger__B | B | plant/tree | WEAK | regen | **REGEN** | 67.8 | opus band WEAK (model said weak); blocking ['STYLE_EARTHLY', 'DESC_MISS', 'ANCHOR']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1', 'K2'], own blocking ['STYLE_EARTHLY'] |
| RM_Dripfringe__B | B | plant/special | WEAK | regen | **REGEN** | 74.7 | opus band WEAK (model said weak); blocking ['ANCHOR', 'STYLE_EARTHLY', 'DESC_MISS']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['ANCHOR'] |
| RM_Fuzzviper__B | B | creature/walker | WEAK | regen | **REGEN** | 89.1 | opus band WEAK (model said good); blocking ['F_TOPDOWN', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_TOPDOWN'] |
| RSW_Anooba__B | B | creature/walker | WEAK | regen | **REGEN** | 120.3 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_INCONSISTENT'] |
| RM_Ghemmel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 34.2 | opus band REALLY_BAD (model said weak); blocking ['DESC_MISS', 'DESC_MISS', 'STYLE_EARTHLY', 'STYLE_CARTOON', 'ANCHOR']; polish ['LEGIB_32'] |
| RSW_Insectomorph__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 41.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_NORTH_FACE', 'DUPLICATE', 'F_INCONSISTENT', 'F_TOPDOWN']; polish [] |
| RSW_Gualaar__A | A | creature/walker | WEAK | regen | **REGEN** | 80.8 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'STYLE_OFF']; polish ['STYLE_EARTHLY']; gpt regen: unsettled ['K2'], own blocking ['STYLE_OFF'] |
| RM_IvvolCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 31.1 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'DESC_MISS', 'STYLE_EARTHLY', 'SIBLING_MISMATCH']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V2ver#1d5b9e+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V2ver#853bd2`
