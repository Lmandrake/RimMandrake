# art_eval run regress_departures_v3c_20261105 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Shadefern | B | plant/bush | GOOD | - | **ACCEPT** | 28.7 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'STYLE_EARTHLY'] |
| RM_Huldu | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 48.9 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'F_TOPDOWN', 'STYLE_CARTOON', 'DESC_MISS', 'F_SIZE_JUMP']; polish [] |
| RM_Ssurr | B | creature/walker | WEAK | regen | **REGEN** | 124.5 | opus band WEAK (model said really_bad); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'DESC_MISS']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'STYLE_CARTOON'] |
| RM_Vellak | B | creature/pack | WEAK | regen | **REGEN** | 115.4 | opus band WEAK (model said really_bad); blocking ['STYLE_EARTHLY', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['STYLE_EARTHLY', 'F_INCONSISTENT'] |
| RM_Murrin | C | creature/swimmer | WEAK | regen | **REGEN** | 109.6 | opus band WEAK (model said weak); blocking ['ALPHA_HALO', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1', 'K2'], own blocking ['ALPHA_HALO'] |
| RM_Dewblade | B | plant/ground_cover | WEAK | unsure | **REGEN** | 97.4 | opus band WEAK (model said really_bad); blocking ['DESC_MISS', 'ANCHOR']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS']; gpt unsure: unsettled ['K1', 'K2'], own blocking ['ANCHOR'] |
| RM_DecayDrake | r2 | creature/walker | WEAK | regen | **REGEN** | 98.7 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'ALPHA_HALO']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'ALPHA_HALO'] |
| RM_Durrok | r2 | creature/walker | WEAK | regen | **REGEN** | 88.4 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'ALPHA_HALO']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'ALPHA_HALO'] |
| RM_Gawpsack | live | creature/walker | WEAK | regen | **REGEN** | 99.6 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Peeper | r2 | creature/walker | REALLY_BAD | - | **REGEN** | 58.5 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'STYLE_EARTHLY']; polish ['LEGIB_32'] |
| RM_Danglemaw | r1 | creature/walker | WEAK | regen | **REGEN** | 107.6 | opus band WEAK (model said really_bad); blocking ['DESC_MISS', 'DEPARTURE_MISSING', 'F_NORTH_FACE']; polish ['LEGIB_32', 'RES_LOW']; gpt regen: unsettled ['K2', 'K3'], own blocking ['DEPARTURE_MISSING', 'F_NORTH_FACE'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+plant@v3#bf05d6`
