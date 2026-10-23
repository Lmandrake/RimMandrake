# art_eval run race_r1d_V1cal_opus_s0 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Fuzzviper__B | B | creature/walker | WEAK | regen | **REGEN** | 91.8 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Mourvel__B | B | plant/tree | WEAK | regen | **REGEN** | 47.1 | opus band WEAK (model said really_bad); blocking ['DESC_MISS']; polish ['STYLE_EARTHLY', 'SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS'] |
| RM_Zhorrel__B | B | plant/tree | WEAK | strong_accept | **ACCEPT** | 47.3 | opus band WEAK (model said good); blocking ['CONSTRUCTED', 'STYLE_EARTHLY']; polish []; gpt strong_accept: unsettled [], own blocking [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V1cal#64d1d9+preamble@v1-V1cal#36a882+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V1cal#f8df95`
