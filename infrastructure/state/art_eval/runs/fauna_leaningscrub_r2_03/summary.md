# art_eval run fauna_leaningscrub_r2_03

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Shokka | r2 | creature/walker | REALLY_BAD | - | **REGEN** | 55.5 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'ALPHA_HALO']; polish ['LEGIB_32'] |
| RM_Surrik | r2 | creature/walker | REALLY_BAD | - | **REGEN** | 63.7 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP', 'F_TOPDOWN', 'DEPARTURE_MISSING', 'ALPHA_HALO', 'STYLE_CARTOON']; polish ['LEGIB_32'] |
| RM_Thornhold | r2 | creature/walker | WEAK | regen | **REGEN** | 119.4 | opus band WEAK (model said good); blocking ['ALPHA_HALO', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['ALPHA_HALO', 'DEPARTURE_MISSING'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
