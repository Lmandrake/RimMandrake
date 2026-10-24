# art_eval run regress_after_tuning_20261024 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Shadefern | B | plant/bush | GOOD | - | **ACCEPT** | 25.9 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'STYLE_EARTHLY', 'SCALE_WRONG'] |
| RM_Huldu | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 55.1 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'STYLE_CARTOON', 'F_INCONSISTENT', 'F_TOPDOWN', 'F_SIZE_JUMP']; polish [] |
| RM_Ssurr | B | creature/walker | REALLY_BAD | - | **REGEN** | 69.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish [] |
| RM_Vellak | B | creature/pack | WEAK | regen | **REGEN** | 115.3 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_EARTHLY']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_INCONSISTENT', 'STYLE_EARTHLY'] |
| RM_Murrin | C | creature/swimmer | WEAK | regen | **REGEN** | 161.3 | opus band WEAK (model said really_bad); blocking ['F_TOPDOWN', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_NORTH_FACE']; polish ['STYLE_EARTHLY', 'LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4', 'K5', 'K7'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_SIZE_JUMP'] |
| RM_Dewblade | B | plant/ground_cover | WEAK | strong_accept | **ACCEPT** | 75.8 | opus band WEAK (model said weak); blocking ['DESC_MISS']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS', 'SCALE_WRONG']; gpt strong_accept: unsettled [], own blocking [] |
| RM_DecayDrake | r2 | creature/walker | WEAK | strong_accept | **ACCEPT** | 96.7 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Durrok | r2 | creature/walker | WEAK | regen | **REGEN** | 89.1 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'ALPHA_HALO', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'ALPHA_HALO'] |
| RM_Gawpsack | live | creature/walker | WEAK | regen | **REGEN** | 92.3 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING'] |
| RM_Peeper | r2 | creature/walker | REALLY_BAD | - | **REGEN** | 53.4 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; polish ['LEGIB_32'] |
| RM_Danglemaw | r1 | creature/walker | WEAK | regen | **REGEN** | 114.6 | opus band WEAK (model said really_bad); blocking ['F_INCONSISTENT', 'F_NORTH_FACE', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K4'], own blocking ['F_INCONSISTENT', 'F_NORTH_FACE'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+plant@v3#bf05d6`
