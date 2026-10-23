# art_eval run fauna_cauldron_02

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Radyak | live | creature/walker | WEAK | regen | **REGEN** | 77.2 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DESC_MISS']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING'] |
| RM_Rhossak | live | creature/walker | WEAK | regen | **REGEN** | 88.7 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['STYLE_EARTHLY', 'LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_SikkaSikka | live | creature/walker | WEAK | strong_accept | **ACCEPT** | 64.2 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING']; polish ['STYLE_EARTHLY']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Suush | live | creature/flyer | REALLY_BAD | - | **REGEN** | 61.1 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DUPLICATE']; polish ['LEGIB_32'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
