# art_eval run fauna_leaningscrub_r1_02

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Tikkit | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 47.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_SOUTH_NOT_FRONT', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'DONOR', 'X_WRONG']; polish ['LEGIB_32'] |
| RM_TunnelSnake | r1 | creature/walker | WEAK | regen | **REGEN** | 124.3 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Vissler | r1 | creature/walker | WEAK | regen | **REGEN** | 116.1 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'F_SIZE_JUMP', 'STYLE_CARTOON']; polish []; gpt regen: unsettled ['K1', 'K2', 'K4'], own blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'F_SIZE_JUMP'] |
| RM_Vurra | r1 | creature/walker | WEAK | regen | **REGEN** | 84.4 | opus band WEAK (model said weak); blocking ['F_SIZE_JUMP']; polish ['F_TOPDOWN', 'STYLE_EARTHLY']; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP'] |
| RM_Zellik | r1 | creature/flyer | REALLY_BAD | - | **REGEN** | 52.6 | opus band REALLY_BAD (model said really_bad); blocking ['ALPHA_HALO', 'DUPLICATE', 'F_SOUTH_NOT_FRONT']; polish []; unreadable ['SOUTH_FRONT'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
