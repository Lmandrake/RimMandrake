# art_eval run race_r1_V1cal_opus_s3 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Karrek__C | C | creature/swimmer | WEAK | regen | **REGEN** | 80.3 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'DEPARTURE_MISSING', 'F_SIZE_JUMP']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_TOPDOWN', 'DEPARTURE_MISSING'] |
| RM_Vellak__B | B | creature/pack | WEAK | regen | **REGEN** | 74.1 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_EARTHLY']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RM_Kirruk__C | C | creature/flyer | REALLY_BAD | - | **REGEN** | 51.4 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['FLYER_WINGS_GROUNDED'] |
| RM_Huldu__B | B | creature/swimmer | REALLY_BAD | - | **REGEN** | 29.0 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'DESC_MISS', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_SIZE_JUMP', 'X_WRONG']; polish [] |
| RM_Dewgourd__B | B | plant/bush | GOOD | - | **ACCEPT** | 30.6 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'STYLE_EARTHLY'] |
| RM_Verdimoss__A | A | plant/ground_cover | GOOD | - | **ACCEPT** | 24.5 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'STYLE_EARTHLY'] |
| Plant_Ambrosia__A | A | plant/bush | REALLY_BAD | - | **REGEN** | 24.4 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DONOR', 'ALPHA_HALO', 'LUMP', 'STYLE_CARTOON']; polish ['LEGIB_32']; unreadable ['VARIANTS'] |
| RSW_Igitz__A | A | creature/amphibious | WEAK | regen | **REGEN** | 64.8 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'DESC_MISS']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RSW_Warbird__A | A | creature/flyer | WEAK | strong_accept | **ACCEPT** | 66.0 | opus band WEAK (model said good); blocking ['DESC_MISS', 'F_INCONSISTENT']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Tumbel__C | C | plant/tree | WEAK | regen | **REGEN** | 57.9 | opus band WEAK (model said really_bad); blocking ['STYLE_EARTHLY', 'DESC_MISS', 'DESC_MISS']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['STYLE_EARTHLY', 'DESC_MISS'] |
| RSW_Kaadu__A | A | creature/walker | WEAK | strong_accept | **ACCEPT** | 67.6 | opus band WEAK (model said good); blocking ['CANON_MISS', 'STYLE_OFF']; polish ['STYLE_EARTHLY']; gpt strong_accept: unsettled [], own blocking [] |
| RM_VizhikCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 21.0 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V1cal#64d1d9+preamble@v1-V1cal#36a882+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V1cal#f8df95`
