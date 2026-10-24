# art_eval run fauna_leaningscrub_r2_01

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Dustflutter | r2 | creature/flyer | WEAK | regen | **REGEN** | 126.3 | opus band WEAK (model said really_bad); blocking ['STYLE_CARTOON', 'STYLE_OFF', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['STYLE_CARTOON', 'STYLE_OFF', 'DEPARTURE_MISSING'] |
| RM_Fuzzrunner | r2 | creature/walker | WEAK | regen | **REGEN** | 126.8 | opus band WEAK (model said good); blocking ['ALPHA_HALO', 'STYLE_CARTOON', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1', 'K3'], own blocking ['ALPHA_HALO', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_OFF'] |
| RM_Fuzzviper | r2 | creature/walker | WEAK | regen | **REGEN** | 151.8 | opus band WEAK (model said weak); blocking ['F_SIZE_JUMP', 'STYLE_CARTOON']; polish ['F_TOPDOWN', 'LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
