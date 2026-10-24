# art_eval run fauna_leaningscrub_r1_01

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Ribbonwhip | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 49.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_SOUTH_NOT_FRONT', 'F_INCONSISTENT', 'ALPHA_HALO', 'DESC_MISS', 'DEPARTURE_MISSING', 'X_WRONG']; polish ['LEGIB_32']; unreadable ['NORTH_REAR'] |
| RM_Rollbug | r1 | creature/walker | WEAK | regen | **REGEN** | 79.2 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'STYLE_EARTHLY']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_INCONSISTENT', 'F_SIZE_JUMP'] |
| RM_Shirrel | r1 | creature/walker | WEAK | regen | **REGEN** | 126.5 | opus band WEAK (model said really_bad); blocking ['F_TOPDOWN', 'F_TOPDOWN', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'F_NORTH_FACE']; polish ['LEGIB_32']; gpt regen: unsettled ['K4'], own blocking ['DEPARTURE_MISSING'] |
| RM_Shokka | r1 | creature/walker | WEAK | regen | **REGEN** | 96.9 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'ALPHA_HALO', 'DEPARTURE_MISSING', 'STYLE_EARTHLY']; polish ['LEGIB_32']; gpt regen: unsettled ['K2', 'K4'], own blocking ['ALPHA_HALO', 'STYLE_EARTHLY'] |
| RM_Surrik | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 49.6 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DONOR', 'F_TOPDOWN', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'X_WRONG']; polish []; unreadable ['SCALE', 'LEGIBLE'] |
| RM_Thornhold | r1 | creature/walker | WEAK | regen | **REGEN** | 71.8 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_SIZE_JUMP']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
