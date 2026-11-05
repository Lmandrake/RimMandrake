# art_eval run regress_departures_v3b_20261105 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Shadefern | B | plant/bush | GOOD | - | **ACCEPT** | 25.7 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'STYLE_EARTHLY'] |
| RM_Huldu | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 54.2 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'F_TOPDOWN', 'STYLE_CARTOON', 'F_SIZE_JUMP', 'DESC_MISS']; polish [] |
| RM_Ssurr | B | creature/walker | REALLY_BAD | - | **REGEN** | 56.0 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_SIZE_JUMP']; polish [] |
| RM_Vellak | B | creature/pack | WEAK | regen | **REGEN** | 122.9 | opus band WEAK (model said really_bad); blocking ['STYLE_EARTHLY', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['STYLE_EARTHLY', 'F_INCONSISTENT'] |
| RM_Murrin | C | creature/swimmer | WEAK | regen | **REGEN** | 116.3 | opus band WEAK (model said weak); blocking ['ALPHA_HALO', 'F_TOPDOWN', 'STYLE_CARTOON']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['ALPHA_HALO', 'F_TOPDOWN'] |
| RM_Dewblade | B | plant/ground_cover | WEAK | regen | **REGEN** | 103.6 | opus band WEAK (model said really_bad); blocking ['DESC_MISS']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS', 'SCALE_WRONG']; gpt regen: unsettled [], own blocking [] |
| RM_DecayDrake | r2 | creature/walker | WEAK | regen | **REGEN** | 95.7 | opus band WEAK (model said good); blocking ['ALPHA_HALO', 'F_SIZE_JUMP']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['ALPHA_HALO', 'F_SIZE_JUMP'] |
| RM_Durrok | r2 | creature/walker | WEAK | regen | **REGEN** | 85.9 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'ALPHA_HALO', 'STYLE_OFF']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'ALPHA_HALO'] |
| RM_Gawpsack | live | creature/walker | WEAK | regen | **REGEN** | 92.8 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Peeper | r2 | creature/walker | WEAK | regen | **REGEN** | 105.1 | opus band WEAK (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP', 'F_NORTH_FACE'] |
| RM_Danglemaw | r1 | creature/walker | WEAK | regen | **REGEN** | 94.1 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING', 'F_NORTH_FACE', 'STYLE_CARTOON']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'F_NORTH_FACE'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#450e15+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+plant@v3#bf05d6`
