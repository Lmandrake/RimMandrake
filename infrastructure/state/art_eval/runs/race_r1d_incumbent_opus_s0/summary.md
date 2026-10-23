# art_eval run race_r1d_incumbent_opus_s0 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Fuzzviper__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 47.2 | opus band REALLY_BAD (model said weak); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_SIZE_JUMP', 'STYLE_EARTHLY']; polish ['F_TOPDOWN', 'LEGIB_32'] |
| RM_Mourvel__B | B | plant/tree | REALLY_BAD | - | **REGEN** | 26.1 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'LUMP']; polish ['STYLE_EARTHLY'] |
| RM_Zhorrel__B | B | plant/tree | WEAK | regen | **REGEN** | 70.4 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'STYLE_OFF', 'DESC_MISS']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1', 'K3'], own blocking ['DESC_MISS'] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
