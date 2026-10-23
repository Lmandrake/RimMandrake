# art_eval run race_r1_incumbent_opus_s3 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Karrek__C | C | creature/swimmer | WEAK | regen | **REGEN** | 122.6 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'DEPARTURE_MISSING', 'F_TOPDOWN']; polish ['STYLE_EARTHLY', 'LEGIB_32']; gpt regen: unsettled ['K2', 'K3'], own blocking ['DEPARTURE_MISSING', 'F_TOPDOWN', 'F_SIZE_JUMP'] |
| RM_Vellak__B | B | creature/pack | REALLY_BAD | - | **REGEN** | 39.1 | opus band REALLY_BAD (model said weak); blocking ['F_INCONSISTENT', 'STYLE_EARTHLY', 'DEPARTURE_MISSING']; polish ['LEGIB_32'] |
| RM_Kirruk__C | C | creature/flyer | REALLY_BAD | - | **REGEN** | 56.1 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'F_TOPDOWN']; polish ['FLYER_WINGS_GROUNDED'] |
| RM_Huldu__B | B | creature/swimmer | REALLY_BAD | - | **REGEN** | 32.5 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'PLACEHOLDER', 'DESC_MISS', 'STYLE_EARTHLY', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish [] |
| RM_Dewgourd__B | B | plant/bush | WEAK | strong_accept | **ACCEPT** | 59.5 | opus band WEAK (model said weak); blocking ['ANCHOR']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS', 'SCALE_WRONG']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Verdimoss__A | A | plant/ground_cover | WEAK | strong_accept | **ACCEPT** | 61.0 | opus band WEAK (model said weak); blocking ['STYLE_CARTOON']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| Plant_Ambrosia__A | A | plant/bush | REALLY_BAD | - | **REGEN** | 27.2 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO', 'CONSTRUCTED', 'LUMP', 'ANCHOR', 'STYLE_CARTOON']; polish ['LEGIB_32', 'WANTS_VARIANTS'] |
| RSW_Igitz__A | A | creature/amphibious | WEAK | regen | **REGEN** | 90.0 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'F_INCONSISTENT']; polish ['SCALE_WRONG', 'LEGIB_32']; gpt regen: unsettled ['K2'], own blocking ['F_INCONSISTENT'] |
| RSW_Warbird__A | A | creature/flyer | WEAK | regen | **REGEN** | 93.7 | opus band WEAK (model said weak); blocking ['ALPHA_HALO', 'DESC_MISS', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish []; gpt regen: unsettled ['K1', 'K3'], own blocking ['ALPHA_HALO', 'F_INCONSISTENT'] |
| RM_Tumbel__C | C | plant/tree | REALLY_BAD | - | **REGEN** | 32.3 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DESC_MISS', 'STYLE_EARTHLY']; polish ['WANTS_VARIANTS'] |
| RSW_Kaadu__A | A | creature/walker | WEAK | regen | **REGEN** | 77.7 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'STYLE_CARTOON', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['STYLE_CARTOON'] |
| RM_VizhikCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 24.1 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'DESC_MISS', 'CATCH_POSE']; polish ['LEGIB_32'] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
