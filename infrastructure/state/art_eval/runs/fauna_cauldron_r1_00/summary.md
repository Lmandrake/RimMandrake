# art_eval run fauna_cauldron_r1_00

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_BedBug | r1 | creature/walker | WEAK | regen | **REGEN** | 90.4 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'F_SIZE_JUMP', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_TOPDOWN'] |
| RM_DecayDrake | r1 | creature/walker | WEAK | regen | **REGEN** | 90.4 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'DEPARTURE_MISSING'] |
| RM_Radyak | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 68.6 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_EARTHLY']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Vexxiss | r1 | creature/walker | WEAK | regen | **REGEN** | 100.7 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING', 'ALPHA_HALO']; polish []; gpt regen: unsettled ['K1', 'K2', 'K4'], own blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'ALPHA_HALO'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
