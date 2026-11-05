# art_eval run regress_departures_v3_20261105 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Shadefern | B | plant/bush | GOOD | - | **ACCEPT** | 21.2 | opus band GOOD (model said good); blocking []; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS'] |
| RM_Huldu | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 47.6 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'STYLE_CARTOON', 'F_TOPDOWN', 'F_SIZE_JUMP']; polish ['LEGIB_32'] |
| RM_Ssurr | B | creature/walker | REALLY_BAD | - | **REGEN** | 53.3 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DESC_MISS', 'STYLE_CARTOON']; polish [] |
| RM_Vellak | B | creature/pack | WEAK | strong_accept | **ACCEPT** | 60.2 | opus band WEAK (model said good); blocking ['STYLE_EARTHLY', 'F_INCONSISTENT']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Murrin | C | creature/swimmer | WEAK | regen | **REGEN** | 95.3 | opus band WEAK (model said weak); blocking ['ALPHA_HALO', 'STYLE_CARTOON']; polish ['STYLE_EARTHLY', 'LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['ALPHA_HALO'] |
| RM_Dewblade | B | plant/ground_cover | WEAK | strong_accept | **ACCEPT** | 73.5 | opus band WEAK (model said really_bad); blocking ['DESC_MISS']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS', 'SCALE_WRONG']; gpt strong_accept: unsettled [], own blocking [] |
| RM_DecayDrake | r2 | creature/walker | WEAK | regen | **REGEN** | 92.9 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'ALPHA_HALO']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'ALPHA_HALO'] |
| RM_Durrok | r2 | creature/walker | WEAK | regen | **REGEN** | 90.1 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'ALPHA_HALO']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'ALPHA_HALO'] |
| RM_Gawpsack | live | creature/walker | WEAK | regen | **REGEN** | 73.1 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Peeper | r2 | creature/walker | REALLY_BAD | - | **REGEN** | 40.6 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; polish ['LEGIB_32'] |
| RM_Danglemaw | r1 | creature/walker | WEAK | regen | **REGEN** | 105.9 | opus band WEAK (model said weak); blocking ['F_NORTH_FACE', 'DESC_MISS', 'STYLE_OFF']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_NORTH_FACE', 'DEPARTURE_MISSING'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+plant@v3#bf05d6`
