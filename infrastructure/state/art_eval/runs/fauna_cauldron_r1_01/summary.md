# art_eval run fauna_cauldron_r1_01

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Bileworm | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 55.0 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish ['F_TOPDOWN'] |
| RM_Eskith | r1 | creature/walker | GOOD | - | **ACCEPT** | 37.3 | opus band GOOD (model said good); blocking []; polish ['LEGIB_32', 'SCALE_WRONG'] |
| RM_Rhossak | r1 | creature/walker | WEAK | regen | **REGEN** | 67.7 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING']; polish ['STYLE_EARTHLY']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING'] |
| RM_Visceral | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 70.6 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP']; polish ['SCALE_WRONG']; gpt strong_accept: unsettled [], own blocking [] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
