# art_eval run flora_contagion_s1

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_AlienTree__AB_OcularTreeA | AB_OcularTreeA | plant/tree | REALLY_BAD | - | **REGEN** | 46.5 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DONOR', 'STYLE_CARTOON']; polish ['STYLE_EARTHLY', 'RES_LOW'] |
| RM_AlienTree__AB_OcularTreeC | AB_OcularTreeC | plant/tree | WEAK | strong_accept | **ACCEPT** | 48.1 | opus band WEAK (model said good); blocking ['STYLE_CARTOON']; polish ['SCALE_WRONG']; gpt strong_accept: unsettled [], own blocking [] |
| RM_Bleedleaf__RM_Bleedleaf | RM_Bleedleaf | plant/bush | WEAK | strong_accept | **ACCEPT** | 51.5 | opus band WEAK (model said weak); blocking []; polish ['SCALE_WRONG', 'STYLE_EARTHLY', 'WANTS_VARIANTS']; gpt strong_accept: unsettled [], own blocking [] |
| RM_DyingCreep__RM_DyingCreep_a | RM_DyingCreep_a | plant/ground_cover | WEAK | regen | **REGEN** | 67.4 | opus band WEAK (model said weak); blocking ['STYLE_CARTOON', 'DESC_MISS']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K2'], own blocking ['DESC_MISS']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_Eyebark__RM_Eyebark_b | RM_Eyebark_b | plant/tree | GOOD | - | **ACCEPT** | 28.4 | opus band GOOD (model said good); blocking []; polish ['LEGIB_32', 'RES_LOW'] |
| RM_Eyebark__RM_Eyebark_d | RM_Eyebark_d | plant/tree | WEAK | strong_accept | **ACCEPT** | 46.8 | opus band WEAK (model said weak); blocking ['STYLE_EARTHLY', 'ANCHOR']; polish ['RES_LOW']; gpt strong_accept: unsettled [], own blocking [] |
| RM_GlobularPlant__AB_GlobularPlant | AB_GlobularPlant | plant/tree | REALLY_BAD | - | **REGEN** | 39.8 | opus band REALLY_BAD (model said really_bad); blocking ['DONOR', 'STYLE_CARTOON', 'DESC_MISS', 'ANCHOR']; polish ['RES_LOW'] |
| RM_HalfAlienTree__AB_HalfAlienTreeA | AB_HalfAlienTreeA | plant/tree | WEAK | regen | **REGEN** | 60.7 | opus band WEAK (model said good); blocking ['ANCHOR']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['ANCHOR'] |
| RM_HalfmadeTree__RM_HalfmadeTree_a | RM_HalfmadeTree_a | plant/tree | WEAK | regen | **REGEN** | 70.4 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'NATURAL']; polish ['RES_LOW']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_HalfmadeTree__RM_HalfmadeTree_c | RM_HalfmadeTree_c | plant/tree | WEAK | regen | **REGEN** | 86.8 | opus band WEAK (model said weak); blocking ['DESC_MISS']; polish ['RES_LOW']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_HalfmadeTreeBlighted__RM_HalfmadeTreeBlighted | RM_HalfmadeTreeBlighted | plant/tree | GOOD | - | **ACCEPT** | 23.1 | opus band GOOD (model said good); blocking []; polish ['RES_LOW'] |
| RM_Meatvine__RM_Meatvine | RM_Meatvine | plant/bush | WEAK | regen | **REGEN** | 52.7 | opus band WEAK (model said good); blocking ['DESC_MISS']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_RedLeaves__GU_RedLeaves | GU_RedLeaves | plant/ground_cover | WEAK | regen | **REGEN** | 63.7 | opus band WEAK (model said good); blocking ['LUMP']; polish ['SCALE_WRONG', 'WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['LUMP'] |
| RM_RustPuff__RustPuff_A | RustPuff_A | plant/bush | - | - | **HOLD_ERROR** | 10.2 | opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles) |
| RM_RustPuff__RustPuff_C | RustPuff_C | plant/bush | - | - | **HOLD_ERROR** | 11.7 | opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles) |
| RM_Sapblister__RM_Sapblister | RM_Sapblister | plant/bush | - | - | **HOLD_ERROR** | 13.3 | opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles) |
| RM_Toothmoss__RM_Toothmoss | RM_Toothmoss | plant/ground_cover | - | - | **HOLD_ERROR** | 13.3 | opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles) |

## One line each for the owner
- RM_RustPuff__RustPuff_A: HOLD_ERROR — opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles)
- RM_RustPuff__RustPuff_C: HOLD_ERROR — opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles)
- RM_Sapblister__RM_Sapblister: HOLD_ERROR — opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles)
- RM_Toothmoss__RM_Toothmoss: HOLD_ERROR — opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles)

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+plant@v2#0469e8`
