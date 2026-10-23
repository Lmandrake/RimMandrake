# art_eval run race_r1_V3own_opus_s1 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Gorrask__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 42.7 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish [] |
| RM_Huldu__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 36.6 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_TOPDOWN', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish ['LEGIB_32'] |
| RM_Murrin__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 41.4 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_INCONSISTENT']; polish ['STYLE_EARTHLY', 'LEGIB_32'] |
| RM_Burrak__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 31.6 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'F_TOPDOWN', 'F_SOUTH_NOT_FRONT', 'F_NORTH_FACE', 'DEPARTURE_MISSING', 'DESC_MISS', 'STYLE_EARTHLY', 'STYLE_CARTOON']; polish [] |
| RM_Bladderquill__B | B | plant/bush | WEAK | strong_accept | **ACCEPT** | 41.3 | opus band WEAK (model said good); blocking ['STYLE_EARTHLY']; polish ['SCALE_WRONG', 'WANTS_VARIANTS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Rockfinger__B | B | plant/tree | WEAK | regen | **REGEN** | 68.1 | opus band WEAK (model said really_bad); blocking ['STYLE_EARTHLY', 'ANCHOR']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['STYLE_EARTHLY'] |
| RM_Dripfringe__B | B | plant/special | WEAK | unsure | **REGEN** | 72.9 | opus band WEAK (model said good); blocking ['ANCHOR', 'FOOTPRINT', 'DESC_MISS']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_Fuzzviper__B | B | creature/walker | WEAK | regen | **REGEN** | 64.0 | opus band WEAK (model said good); blocking ['F_TOPDOWN']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_TOPDOWN'] |
| RSW_Anooba__B | B | creature/walker | WEAK | regen | **REGEN** | 90.8 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'F_INCONSISTENT'] |
| RM_Ghemmel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 28.4 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY', 'STYLE_CARTOON']; polish ['WANTS_VARIANTS'] |
| RSW_Insectomorph__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 37.0 | opus band REALLY_BAD (model said really_bad); blocking ['F_NORTH_FACE', 'F_INCONSISTENT', 'DUPLICATE']; polish ['LEGIB_32'] |
| RSW_Gualaar__A | A | creature/walker | WEAK | regen | **REGEN** | 58.9 | opus band WEAK (model said good); blocking ['STYLE_OFF']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['STYLE_OFF'] |
| RM_IvvolCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 26.2 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'STYLE_EARTHLY', 'DESC_MISS', 'SIBLING_MISMATCH']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V3own#33f5d7+preamble@v1-V3own#b2a1a8+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
