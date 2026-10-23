# art_eval run race_r1g_V1cal_gpt_s1 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Gorrask__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 86.7 | opus band REALLY_BAD (model said good); blocking ['DEPARTURE_MISSING']; polish [] |
| RM_Ssurr__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 91.4 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish []; unreadable ['SAME_SIZE', 'OURS'] |
| RM_Kirruk__C | C | creature/flyer | REALLY_BAD | - | **REGEN** | 81.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'DEPARTURE_MISSING', 'X_CROP']; polish ['FLYER_WINGS_GROUNDED']; unreadable ['OURS'] |
| RM_Shadefern__B | B | plant/bush | WEAK | unsure | **REGEN** | 64.5 | opus band WEAK (model said really_bad); blocking []; polish ['STYLE_EARTHLY']; unreadable ['VARIANTS']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_Rockfinger__B | B | plant/tree | WEAK | regen | **REGEN** | 75.4 | opus band WEAK (model said weak); blocking ['STYLE_EARTHLY']; polish []; unreadable ['OURS']; gpt regen: unsettled ['K1', 'K2'], own blocking ['STYLE_EARTHLY'] |
| Plant_Ambrosia__B | B | plant/bush | REALLY_BAD | - | **REGEN** | 33.5 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO']; polish []; unreadable ['OURS', 'VARIANTS'] |
| RSW_Mudhorn__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 76.2 | opus band REALLY_BAD (model said good); blocking ['F_SIZE_JUMP', 'ALPHA_HALO', 'X_CROP']; polish []; unreadable ['OURS'] |
| RM_Ghemmel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 40.9 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS']; polish []; unreadable ['OURS'] |
| RSW_JungleRancor__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 89.6 | opus band REALLY_BAD (model said really_bad); blocking ['CANON_MISS', 'CANON_MISS', 'DESC_MISS', 'ALPHA_HALO']; polish []; unreadable ['OURS'] |
| RM_VizhikCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 41.6 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE']; polish []; unreadable ['SIGNATURE', 'SCALE'] |

Models reported: gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V1cal#64d1d9+preamble@v1-V1cal#36a882+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V1cal#f8df95`
