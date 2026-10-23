# art_eval run race_r1g_V1cal_gpt_s3 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Karrek__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 68.6 | opus band REALLY_BAD (model said good); blocking ['F_SIZE_JUMP']; polish ['LEGIB_32']; unreadable ['OURS'] |
| RM_Loomu__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 81.6 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish []; unreadable ['NO_OVERHEAD', 'DEPARTURES'] |
| RM_Burrak__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 91.3 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'DONOR']; polish [] |
| RM_Dewblade__B | B | plant/ground_cover | WEAK | unsure | **REGEN** | 69.3 | opus band WEAK (model said good); blocking []; polish ['SCALE_WRONG', 'LEGIB_32']; unreadable ['OURS', 'VARIANTS']; gpt unsure: unsettled ['K1', 'K2'], own blocking [] |
| RM_Verdimoss__A | A | plant/ground_cover | WEAK | unsure | **REGEN** | 52.4 | opus band WEAK (model said good); blocking []; polish []; unreadable ['VARIANTS']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_Fuzzviper__B | B | creature/walker | WEAK | unsure | **REGEN** | 111.3 | opus band WEAK (model said weak); blocking []; polish []; unreadable ['NO_OVERHEAD', 'OURS']; gpt unsure: unsettled ['K2'], own blocking [] |
| RSW_Rancor__A | A | creature/walker | WEAK | strong_accept | **ACCEPT** | 148.1 | opus band WEAK (model said good); blocking []; polish []; unreadable ['OURS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Tumbel__C | C | plant/tree | WEAK | strong_accept | **ACCEPT** | 73.5 | opus band WEAK (model said good); blocking []; polish []; unreadable ['OURS']; gpt strong_accept: unsettled [], own blocking [] |
| RSW_MastiffPhalone__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 68.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'CANON_MISS']; polish []; unreadable ['OURS'] |
| RM_HulduCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 39.4 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE']; polish []; unreadable ['SIGNATURE', 'SCALE'] |

Models reported: gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V1cal#64d1d9+preamble@v1-V1cal#36a882+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V1cal#f8df95`
