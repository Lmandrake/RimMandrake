# art_eval run race_r1g_V1cal_gpt_s2 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ivvol__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 66.0 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish [] |
| RM_Vellak__B | B | creature/pack | WEAK | strong_accept | **ACCEPT** | 64.9 | opus band WEAK (model said good); blocking []; polish []; unreadable ['OURS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Gorrask__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 74.5 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'STYLE_OFF', 'DONOR']; polish ['STYLE_EARTHLY', 'SCALE_WRONG'] |
| RM_Bladderquill__B | B | plant/bush | WEAK | unsure | **REGEN** | 65.7 | opus band WEAK (model said good); blocking []; polish ['SCALE_WRONG']; unreadable ['VARIANTS']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_Steamfrond__A | A | plant/bush | WEAK | unsure | **REGEN** | 45.9 | opus band WEAK (model said good); blocking []; polish []; unreadable ['VARIANTS']; gpt unsure: unsettled ['K1'], own blocking [] |
| Plant_Ambrosia__A | A | plant/bush | REALLY_BAD | - | **REGEN** | 42.4 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO', 'DONOR']; polish []; unreadable ['VARIANTS'] |
| RSW_Anooba__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 83.7 | opus band REALLY_BAD (model said really_bad); blocking ['CANON_MISS', 'CANON_MISS', 'CANON_MISS', 'F_SIZE_JUMP']; polish []; unreadable ['OURS'] |
| RM_Mourvel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 44.1 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY']; polish []; unreadable ['OURS'] |
| RSW_Kaadu__A | A | creature/walker | WEAK | strong_accept | **ACCEPT** | 58.0 | opus band WEAK (model said good); blocking []; polish []; unreadable ['OURS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_LoomuCatch__A | A | creature/catch | REALLY_BAD | - | **REGEN** | 29.5 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_CARTOON', 'DONOR', 'CATCH_WRONG']; polish []; unreadable ['SIGNATURE', 'ALIEN', 'SCALE'] |

Models reported: gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V1cal#64d1d9+preamble@v1-V1cal#36a882+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V1cal#f8df95`
