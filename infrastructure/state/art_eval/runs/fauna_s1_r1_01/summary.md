# art_eval run fauna_s1_r1_01

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Fuzzrunner | s1r1 | creature/walker | WEAK | regen | **REGEN** | 72.4 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING'] |
| RM_Surrik | s1r1 | creature/walker | REALLY_BAD | - | **REGEN** | 58.1 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_EARTHLY']; polish ['LEGIB_32'] |
| RM_Peeper | s1r1 | creature/walker | WEAK | regen | **REGEN** | 98.8 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'STYLE_EARTHLY']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
