# art_eval run gptredo_00

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Harrok | live | creature/walker | WEAK | regen | **REGEN** | 77.7 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING'] |
| RM_Mirrak | live | creature/walker | WEAK | regen | **REGEN** | 116.8 | opus band WEAK (model said really_bad); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_EARTHLY', 'DESC_MISS', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4', 'K5', 'K6'], own blocking [] |
| RM_Pirrik | live | creature/flyer | REALLY_BAD | - | **REGEN** | 47.4 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DEPARTURE_MISSING']; polish ['FLYER_WINGS_GROUNDED', 'SCALE_WRONG'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
