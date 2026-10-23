# art_eval run race_r1c_V3own_opus_s0 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_Convor__A | A | creature/flyer | REALLY_BAD | - | **REGEN** | 34.8 | opus band REALLY_BAD (model said good); blocking ['CANON_MISS', 'CANON_MISS']; polish ['SCALE_WRONG'] |
| RSW_Anooba__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 35.2 | opus band REALLY_BAD (model said really_bad); blocking ['CANON_MISS', 'CANON_MISS', 'CANON_MISS', 'F_SIZE_JUMP']; polish [] |
| RSW_Nexu__A | A | creature/walker | WEAK | strong_accept | **ACCEPT** | 82.3 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'STYLE_CARTOON']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RSW_Kaadu__A | A | creature/walker | WEAK | regen | **REGEN** | 83.7 | opus band WEAK (model said good); blocking ['CANON_MISS', 'CANON_MISS', 'F_INCONSISTENT']; polish ['STYLE_EARTHLY']; gpt regen: unsettled ['K1'], own blocking ['CANON_MISS'] |
| RSW_KellDragon__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 38.5 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_NORTH_FACE', 'F_SIZE_JUMP', 'F_INCONSISTENT']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V3own#33f5d7+preamble@v1-V3own#b2a1a8+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
