# art_eval run regress_20261024T014853 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Shadefern | B | plant/bush | GOOD | - | **ACCEPT** | 40.0 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'STYLE_EARTHLY', 'LEGIB_32'] |
| RM_Huldu | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 45.2 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'F_TOPDOWN', 'STYLE_CARTOON']; polish ['LEGIB_32'] |
| RM_Ssurr | B | creature/walker | REALLY_BAD | - | **REGEN** | 60.8 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'STYLE_CARTOON', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish [] |
| RM_Vellak | B | creature/pack | WEAK | regen | **REGEN** | 90.1 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'STYLE_EARTHLY']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RM_Murrin | C | creature/swimmer | WEAK | regen | **REGEN** | 119.1 | opus band WEAK (model said weak); blocking ['DEPARTURE_MISSING', 'F_TOPDOWN', 'F_INCONSISTENT', 'STYLE_CARTOON', 'DEPARTURE_MISSING']; polish ['STYLE_EARTHLY', 'SCALE_WRONG']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4', 'K5'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_TOPDOWN', 'DEPARTURE_MISSING', 'STYLE_CARTOON'] |
| RM_Dewblade | B | plant/ground_cover | WEAK | unsure | **REGEN** | 85.9 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'DESC_MISS']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS', 'SCALE_WRONG']; gpt unsure: unsettled ['K1'], own blocking [] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+plant@v3#bf05d6`
