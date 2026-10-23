# art_eval run fauna_pyrelands_a

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_FireHawk | live | creature/flyer | REALLY_BAD | - | **REGEN** | 73.4 | opus band REALLY_BAD (model said weak); blocking ['DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'F_NORTH_FACE', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'FLYER_BODY_MOVES', 'SIBLING_MISMATCH']; polish ['STYLE_EARTHLY'] |
| RM_FurnaceBeast | live | creature/walker | WEAK | regen | **REGEN** | 107.2 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING', 'DESC_MISS', 'DEPARTURE_MISSING', 'STYLE_OFF']; polish ['MATERIAL_PAINT', 'RES_LOW']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Ullai | live | creature/walker | REALLY_BAD | - | **REGEN** | 54.8 | opus band REALLY_BAD (model said weak); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DESC_MISS']; polish ['SCALE_WRONG'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
