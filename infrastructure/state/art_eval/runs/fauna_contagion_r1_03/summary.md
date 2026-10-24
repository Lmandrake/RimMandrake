# art_eval run fauna_contagion_r1_03

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Peeper | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 45.8 | opus band REALLY_BAD (model said really_bad); blocking ['DEPARTURE_MISSING', 'STYLE_EARTHLY', 'DESC_MISS', 'DEPARTURE_MISSING', 'F_SIZE_JUMP']; polish ['LEGIB_32'] |
| RM_Scaldhide | r1 | creature/walker | WEAK | regen | **REGEN** | 90.0 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_SOUTH_NOT_FRONT']; polish []; unreadable ['SOUTH_FRONT']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4', 'K5'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Scorchpod | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 51.8 | opus band WEAK (model said good); blocking ['DUPLICATE']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Skinflap | r1 | creature/flyer | WEAK | strong_accept | **ACCEPT** | 52.9 | opus band WEAK (model said good); blocking ['DUPLICATE']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Sloshbelly | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 64.9 | opus band WEAK (model said good); blocking ['F_TOPDOWN']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Sparkleech | r1 | creature/flyer | WEAK | regen | **REGEN** | 61.8 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish ['LEGIB_32', 'FLYER_WINGS_GROUNDED']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v3#fdc520`
