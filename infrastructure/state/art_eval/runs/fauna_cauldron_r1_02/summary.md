# art_eval run fauna_cauldron_r1_02

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_CrystalMit | r1 | creature/walker | WEAK | regen | **REGEN** | 77.6 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'F_SIZE_JUMP']; polish []; gpt regen: unsettled ['K2'], own blocking ['F_SIZE_JUMP'] |
| RM_Mullgoth | r1 | creature/walker | WEAK | regen | **REGEN** | 75.0 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Suush | r1 | creature/flyer | WEAK | unsure | **REGEN** | 77.9 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'STYLE_OFF']; polish ['LEGIB_32']; gpt unsure: unsettled ['K1', 'K2'], own blocking ['STYLE_OFF'] |
| RM_Zisska | r1 | creature/walker | WEAK | regen | **REGEN** | 104.4 | opus band WEAK (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K2', 'K3', 'K4', 'K5'], own blocking ['DEPARTURE_MISSING', 'F_INCONSISTENT', 'F_SIZE_JUMP'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
