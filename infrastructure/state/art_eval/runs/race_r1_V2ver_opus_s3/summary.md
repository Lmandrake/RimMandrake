# art_eval run race_r1_V2ver_opus_s3 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Karrek__C | C | creature/swimmer | WEAK | regen | **REGEN** | 125.1 | opus band WEAK (model said weak); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'F_TOPDOWN', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4'], own blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'F_TOPDOWN', 'DEPARTURE_MISSING'] |
| RM_Vellak__B | B | creature/pack | REALLY_BAD | - | **REGEN** | 49.3 | opus band REALLY_BAD (model said weak); blocking ['STYLE_EARTHLY', 'F_INCONSISTENT', 'DEPARTURE_MISSING', 'STYLE_CARTOON']; polish [] |
| RM_Kirruk__C | C | creature/flyer | REALLY_BAD | - | **REGEN** | 67.5 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'F_SIZE_JUMP', 'F_TOPDOWN', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT']; polish ['FLYER_WINGS_GROUNDED'] |
| RM_Huldu__B | B | creature/swimmer | REALLY_BAD | - | **REGEN** | 37.4 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'DESC_MISS', 'DEPARTURE_MISSING', 'STYLE_EARTHLY', 'STYLE_CARTOON', 'F_SIZE_JUMP', 'X_WRONG']; polish [] |
| RM_Dewgourd__B | B | plant/bush | WEAK | regen | **REGEN** | 61.7 | opus band WEAK (model said weak); blocking ['ANCHOR']; polish ['STYLE_EARTHLY', 'STYLE_EARTHLY', 'WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['ANCHOR'] |
| RM_Verdimoss__A | A | plant/ground_cover | WEAK | strong_accept | **ACCEPT** | 78.9 | opus band WEAK (model said weak); blocking ['ANCHOR', 'ALPHA_HALO', 'DESC_MISS']; polish ['LEGIB_32', 'WANTS_VARIANTS', 'STYLE_EARTHLY']; gpt strong_accept: unsettled [], own blocking [] |
| Plant_Ambrosia__A | A | plant/bush | REALLY_BAD | - | **REGEN** | 31.5 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'ALPHA_HALO', 'STYLE_CARTOON', 'ANCHOR', 'LUMP', 'DONOR']; polish ['LEGIB_32', 'WANTS_VARIANTS']; unreadable ['OURS'] |
| RSW_Igitz__A | A | creature/amphibious | REALLY_BAD | - | **REGEN** | 45.6 | opus band REALLY_BAD (model said weak); blocking ['F_INCONSISTENT', 'DESC_MISS']; polish ['SCALE_WRONG']; unreadable ['SIGNATURE'] |
| RSW_Warbird__A | A | creature/flyer | WEAK | regen | **REGEN** | 85.5 | opus band WEAK (model said weak); blocking ['ALPHA_HALO', 'STYLE_CARTOON', 'DESC_MISS']; polish []; gpt regen: unsettled ['K1'], own blocking ['ALPHA_HALO'] |
| RM_Tumbel__C | C | plant/tree | REALLY_BAD | - | **REGEN** | 34.8 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DESC_MISS', 'STYLE_EARTHLY']; polish ['WANTS_VARIANTS'] |
| RSW_Kaadu__A | A | creature/walker | WEAK | regen | **REGEN** | 87.9 | opus band WEAK (model said weak); blocking ['CANON_MISS', 'STYLE_CARTOON', 'F_INCONSISTENT']; polish ['STYLE_EARTHLY']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['STYLE_CARTOON'] |
| RM_VizhikCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 37.3 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE', 'STYLE_EARTHLY', 'DESC_MISS', 'SIBLING_MISMATCH']; polish ['LEGIB_32'] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1-V2ver#1d5b9e+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2-V2ver#853bd2`
