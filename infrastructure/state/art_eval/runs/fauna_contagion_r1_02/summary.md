# art_eval run fauna_contagion_r1_02

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Gorekite | r1 | creature/flyer | WEAK | regen | **REGEN** | 83.2 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_EARTHLY']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RM_InfectedAerofleet | r1 | creature/walker | GOOD | - | **ACCEPT** | 29.3 | opus band GOOD (model said good); blocking []; polish ['LEGIB_32'] |
| RM_Meltgut | r1 | creature/walker | WEAK | regen | **REGEN** | 105.6 | opus band WEAK (model said really_bad); blocking ['F_NORTH_FACE', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'DESC_MISS', 'DEPARTURE_MISSING']; polish ['F_TOPDOWN', 'SCALE_WRONG']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K5'], own blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING'] |
| RM_OcularJelly | r1 | creature/walker | WEAK | regen | **REGEN** | 70.6 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'STYLE_CARTOON', 'DESC_MISS']; polish []; gpt regen: unsettled ['K3'], own blocking ['DESC_MISS'] |
| RM_Ogleknot | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 74.8 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
