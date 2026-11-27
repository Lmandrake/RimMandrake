# art_eval run owedfaces_20261127

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Fessu__faces | r1 | creature/swimmer | WEAK | regen | **REGEN** | 142.7 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'F_TOPDOWN', 'F_SOUTH_NOT_FRONT', 'OWNER_NOTE_IGNORED', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4', 'K5'], own blocking ['F_INCONSISTENT', 'F_TOPDOWN', 'DEPARTURE_MISSING'] |
| RM_Hesuun__faces | r1 | creature/walker | WEAK | regen | **REGEN** | 100.3 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP'] |
| RM_Krellik__faces | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 77.9 | opus band WEAK (model said good); blocking ['F_SOUTH_NOT_FRONT', 'DUPLICATE']; polish []; unreadable ['SOUTH_FRONT']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Oddu__faces | r1 | creature/walker | WEAK | regen | **REGEN** | 132.8 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'OWNER_NOTE_IGNORED', 'F_SIZE_JUMP', 'STYLE_EARTHLY']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4', 'K5'], own blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'OWNER_NOTE_IGNORED', 'STYLE_EARTHLY'] |
| RM_Oovanam__faces | r1 | creature/walker | WEAK | regen | **REGEN** | 103.0 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'STYLE_EARTHLY']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'STYLE_EARTHLY'] |
| RM_Oovu__faces | r1 | creature/walker | - | - | **REGEN** | 0.8 | facing truth FLAG (facing_scale_lint gate, plan serpent): south d_south 0.444 (band 0.64..1.52); south feet -0.2656 (band -0.03..0.03) |
| RM_Tarnn__faces | r1 | creature/walker | WEAK | regen | **REGEN** | 98.6 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'OWNER_NOTE_IGNORED']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking [] |
| RM_Zhiil__faces | r1 | creature/swimmer | WEAK | strong_accept | **ACCEPT** | 81.1 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'F_TOPDOWN', 'DEPARTURE_MISSING']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Tarruq__faces | r1 | creature/walker | - | - | **REGEN** | 0.9 | facing truth FLAG (facing_scale_lint gate, plan biped): south feet 0.0703 (band -0.03..0.03); north feet 0.0742 (band -0.03..0.03) |
| RSW_Moornak__faces | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 56.8 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RSW_Onnik__faces | r1 | creature/walker | WEAK | regen | **REGEN** | 82.4 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RSW_SandStalker__faces | r1 | creature/walker | WEAK | regen | **REGEN** | 123.0 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'OWNER_NOTE_IGNORED']; polish []; gpt regen: unsettled ['K2', 'K3'], own blocking ['F_SIZE_JUMP'] |

Models reported: UNMEASURED, claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v3#50b472+gpt_targeted_second_look@v2#4640d0+opus_first_pass@v3#d22c47+preamble@v4#815246+regen_prompt_edit@v2#209449+severity@v6#6f57c5+creature@v5#78b1be`
