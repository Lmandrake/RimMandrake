# art_eval run fauna_auto_20261028_1101

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_FireHawk | r1 | creature/flyer | WEAK | regen | **REGEN** | 82.3 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RM_FireWasp | r1 | creature/flyer | WEAK | regen | **REGEN** | 88.4 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['SCALE_WRONG', 'FLYER_WINGS_GROUNDED']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_TOPDOWN', 'DEPARTURE_MISSING'] |
| RM_Flamefang | r2 | creature/walker | REALLY_BAD | - | **REGEN** | 53.9 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT']; polish ['STYLE_EARTHLY'] |
| RM_FurnaceBeast | r2 | creature/walker | WEAK | strong_accept | **ACCEPT** | 132.6 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_CARTOON']; polish []; gpt strong_accept: unsettled [], own blocking [] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
