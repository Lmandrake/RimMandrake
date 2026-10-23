# art_eval run race_r1g_incumbent_gpt_s2 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ivvol__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 85.2 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish [] |
| RM_Vellak__B | B | creature/pack | GOOD | - | **ACCEPT** | 55.9 | opus band GOOD (model said good); blocking []; polish [] |
| RM_Gorrask__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 72.4 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'STYLE_OFF', 'DONOR']; polish ['STYLE_EARTHLY', 'SCALE_WRONG'] |
| RM_Bladderquill__B | B | plant/bush | WEAK | unsure | **REGEN** | 59.3 | opus band WEAK (model said weak); blocking []; polish ['SCALE_WRONG']; unreadable ['VARIANTS']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_Steamfrond__A | A | plant/bush | WEAK | unsure | **REGEN** | 67.4 | opus band WEAK (model said weak); blocking []; polish []; unreadable ['VARIANTS']; gpt unsure: unsettled ['K1'], own blocking [] |
| Plant_Ambrosia__A | A | plant/bush | REALLY_BAD | - | **REGEN** | 48.2 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'LUMP', 'ALPHA_HALO', 'DONOR']; polish ['LEGIB_32']; unreadable ['ANCHOR', 'VARIANTS'] |
| RSW_Anooba__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 109.0 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'CANON_MISS', 'CANON_MISS', 'CANON_MISS', 'CANON_MISS']; polish []; unreadable ['OURS'] |
| RM_Mourvel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 42.0 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'STYLE_EARTHLY']; polish []; unreadable ['OURS'] |
| RSW_Kaadu__A | A | creature/walker | WEAK | regen | **REGEN** | 105.9 | opus band WEAK (model said weak); blocking []; polish []; unreadable ['OURS']; gpt regen: unsettled [], own blocking ['CANON_MISS'] |
| RM_LoomuCatch__A | A | creature/catch | REALLY_BAD | - | **REGEN** | 26.6 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'STYLE_CARTOON', 'DONOR', 'CATCH_WRONG']; polish []; unreadable ['SIGNATURE', 'SCALE', 'CATCH_DEAD'] |

Models reported: gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
