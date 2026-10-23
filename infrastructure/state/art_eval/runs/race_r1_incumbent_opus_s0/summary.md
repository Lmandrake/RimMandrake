# art_eval run race_r1_incumbent_opus_s0 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Burrak__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 49.3 | opus band REALLY_BAD (model said weak); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT', 'F_TOPDOWN', 'F_SIZE_JUMP']; polish ['LEGIB_32'] |
| RM_Sillik__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 44.4 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'STYLE_CARTOON', 'F_NORTH_FACE', 'F_SIZE_JUMP']; polish ['F_TOPDOWN', 'LEGIB_32'] |
| RM_Loomu__C | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 50.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_TOPDOWN', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'STYLE_CARTOON', 'DEPARTURE_MISSING']; polish ['LEGIB_32'] |
| RM_Gorrask__B | B | creature/walker | REALLY_BAD | - | **REGEN** | 31.3 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'DESC_MISS', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'STYLE_CARTOON', 'F_SIZE_JUMP']; polish ['STYLE_EARTHLY', 'SCALE_WRONG'] |
| RM_Shadefern__B | B | plant/bush | WEAK | regen | **REGEN** | 54.3 | opus band WEAK (model said weak); blocking ['ANCHOR']; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['ANCHOR', 'DESC_MISS'] |
| RM_Salvecomb__B | B | plant/bush | WEAK | regen | **REGEN** | 59.8 | opus band WEAK (model said weak); blocking ['ANCHOR', 'STYLE_CARTOON']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['ANCHOR'] |
| RM_Weepmat__A | A | plant/ground_cover | WEAK | regen | **REGEN** | 72.5 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'LUMP', 'ALPHA_HALO', 'STYLE_CARTOON']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['DESC_MISS', 'LUMP', 'ALPHA_HALO'] |
| RSW_Mudhorn__C | C | creature/walker | REALLY_BAD | - | **REGEN** | 40.0 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP', 'STYLE_OFF', 'X_CROP']; polish ['LEGIB_32'] |
| RSW_Nexu__A | A | creature/walker | WEAK | regen | **REGEN** | 90.4 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP', 'STYLE_CARTOON']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP'] |
| RM_Zhorrel__B | B | plant/tree | WEAK | regen | **REGEN** | 58.0 | opus band WEAK (model said good); blocking ['DESC_MISS', 'DESC_MISS', 'CONSTRUCTED']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['DESC_MISS'] |
| RSW_MastiffPhalone__A | A | creature/walker | REALLY_BAD | - | **REGEN** | 46.9 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP', 'DESC_MISS', 'DESC_MISS', 'DESC_MISS']; polish ['SCALE_WRONG'] |
| RM_HulduCatch__C | C | creature/catch | REALLY_BAD | - | **REGEN** | 26.3 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'CATCH_POSE', 'STYLE_EARTHLY', 'SIBLING_MISMATCH']; polish ['LEGIB_32'] |
| RM_LoomuCatch__A | A | creature/catch | REALLY_BAD | - | **REGEN** | 25.2 | opus band REALLY_BAD (model said really_bad); blocking ['CATCH_WRONG', 'DONOR', 'CATCH_POSE', 'DESC_MISS', 'STYLE_EARTHLY', 'STYLE_CARTOON']; polish [] |

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+creature@v2#16a385`
