# art_eval run race_r1_V3own_opus_s3 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Karrek__C | C | creature/swimmer | WEAK | regen | **REGEN** | 75.0 | opus band WEAK (model said good); blocking ['F_TOPDOWN', 'DEPARTURE_MISSING']; polish ['LEGIB_32', 'STYLE_EARTHLY']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_TOPDOWN', 'DEPARTURE_MISSING'] |
| RM_Vellak__B | B | creature/pack | REALLY_BAD | - | **REGEN** | 39.7 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'F_INCONSISTENT']; polish ['LEGIB_32'] |
| RM_Kirruk__C | C | creature/flyer | REALLY_BAD | - | **REGEN** | 55.2 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'X_CROP']; polish ['FLYER_WINGS_GROUNDED'] |
| RM_Huldu__B | B | creature/swimmer | REALLY_BAD | - | **REGEN** | 30.8 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'PLACEHOLDER', 'DESC_MISS', 'DEPARTURE_MISSING', 'STYLE_EARTHLY', 'STYLE_CARTOON']; polish ['RES_LOW'] |
| RM_Dewgourd__B | B | plant/bush | WEAK | strong_accept | **ACCEPT** | 46.7 | opus band WEAK (model said good); blocking ['ANCHOR']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Verdimoss__A | A | plant/ground_cover | WEAK | strong_accept | **ACCEPT** | 33.0 | opus band WEAK (model said good); blocking ['DESC_MISS']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| Plant_Ambrosia__A | A | plant/bush | REALLY_BAD | - | **REGEN** | 24.4 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO', 'CONSTRUCTED', 'LUMP', 'STYLE_CARTOON']; polish ['LEGIB_32', 'WANTS_VARIANTS'] |
| RSW_Igitz__A | A | creature/amphibious | WEAK | regen | **REGEN** | 78.2 | opus band WEAK (model said good); blocking ['DESC_MISS', 'F_INCONSISTENT']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K2'], own blocking ['F_INCONSISTENT'] |
| RSW_Warbird__A | A | creature/flyer | WEAK | regen | **REGEN** | 91.2 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'ALPHA_HALO']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['ALPHA_HALO'] |
| RM_Tumbel__C | C | plant/tree | REALLY_BAD | - | **REGEN** | 26.3 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY']; polish [] |
| RSW_Kaadu__A | A | creature/walker | WEAK | strong_accept | **ACCEPT** | 66.9 | opus band WEAK (model said good); blocking ['CANON_MISS', 'STYLE_CARTOON']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_VizhikCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 21.2 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE', 'DESC_MISS']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V3own#33f5d7+preamble@v1-V3own#b2a1a8+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
