# art_eval run race_r1g_incumbent_gpt_s3 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Karrek__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 86.8 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'DESC_MISS', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; unreadable ['OURS'] |
| RM_Loomu__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 117.2 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish []; unreadable ['DEPARTURES', 'OURS'] |
| RM_Burrak__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 95.0 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'DESC_MISS', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'STYLE_OFF', 'DONOR']; polish [] |
| RM_Dewblade__B | B | plant/ground_cover | WEAK | unsure | **REGEN** | 62.1 | opus band WEAK (model said weak); blocking []; polish ['STYLE_EARTHLY', 'SCALE_WRONG']; unreadable ['VARIANTS']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_Verdimoss__A | A | plant/ground_cover | WEAK | unsure | **REGEN** | 42.7 | opus band WEAK (model said weak); blocking []; polish []; unreadable ['VARIANTS']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_Fuzzviper__B | B | creature/walker | WEAK | regen | **REGEN** | 126.8 | opus band WEAK (model said weak); blocking ['F_TOPDOWN']; polish ['LEGIB_32']; unreadable ['OURS', 'SCALE']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_TOPDOWN'] |
| RSW_Rancor__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 86.2 | opus band REALLY_BAD (model said weak); blocking ['STYLE_CARTOON', 'ALPHA_HALO']; polish []; unreadable ['OURS'] |
| RM_Tumbel__C | C | plant/tree | REALLY_BAD | - | **REGEN** | 58.2 | opus band REALLY_BAD (model said weak); blocking ['DESC_MISS']; polish []; unreadable ['OURS'] |
| RSW_MastiffPhalone__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 91.2 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP', 'CANON_MISS']; polish []; unreadable ['OURS'] |
| RM_HulduCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 41.0 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE']; polish []; unreadable ['SIGNATURE', 'SCALE'] |

Models reported: gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
