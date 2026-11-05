# art_eval run audit_20261105_g8

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Skarrin_n | r2 | creature/swimmer | REALLY_BAD | - | **REGEN** | 69.3 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_NORTH_FACE', 'F_INCONSISTENT', 'OWNER_NOTE_IGNORED']; polish ['LEGIB_32'] |
| RM_Vhakk_n | r2 | creature/walker | WEAK | strong_accept | **ACCEPT** | 58.9 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'F_SIZE_JUMP']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Vizhik_ns | r2 | creature/walker | WEAK | strong_accept | **ACCEPT** | 92.0 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING']; polish ['F_TOPDOWN', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
