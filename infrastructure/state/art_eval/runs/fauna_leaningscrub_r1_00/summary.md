# art_eval run fauna_leaningscrub_r1_00

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Chikka | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 51.2 | opus band REALLY_BAD (model said really_bad); blocking ['DEPARTURE_MISSING', 'F_SOUTH_NOT_FRONT', 'DESC_MISS', 'F_SIZE_JUMP', 'F_INCONSISTENT']; polish ['SCALE_WRONG'] |
| RM_Crustweevil | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 50.7 | opus band REALLY_BAD (model said really_bad); blocking ['F_SOUTH_NOT_FRONT', 'F_INCONSISTENT', 'DONOR', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'X_WRONG']; polish ['LEGIB_32'] |
| RM_Durrok | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 41.9 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DEPARTURE_MISSING', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish [] |
| RM_Dustflutter | r1 | creature/flyer | REALLY_BAD | - | **REGEN** | 54.6 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'DONOR', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'X_WRONG', 'X_CROP']; polish ['SCALE_WRONG']; unreadable ['SCALE', 'LEGIBLE'] |
| RM_Fuzzrunner | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 48.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'DONOR', 'DEPARTURE_MISSING', 'F_SIZE_JUMP', 'STYLE_EARTHLY', 'X_WRONG']; polish ['SCALE_WRONG']; unreadable ['SCALE', 'LEGIBLE'] |
| RM_Fuzzviper | r1 | creature/walker | WEAK | regen | **REGEN** | 85.2 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
