# art_eval run fin_plants_20261107

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Iashiphus | fin1 | plant/bush | WEAK | strong_accept | **ACCEPT** | 56.5 | opus band WEAK (model said good); blocking ['STYLE_CARTOON']; polish ['WANTS_VARIANTS', 'SCALE_WRONG']; gpt strong_accept: unsettled [], own blocking [] |
| RM_PoisonShrub__ShrubLowA | fin1 | plant/bush | WEAK | strong_accept | **ACCEPT** | 45.7 | opus band WEAK (model said good); blocking ['STYLE_CARTOON']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_PoisonShrub__ShrubLowB | fin1 | plant/bush | WEAK | strong_accept | **ACCEPT** | 55.8 | opus band WEAK (model said good); blocking ['STYLE_CARTOON', 'SIBLING_MISMATCH']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_SugarFamewort | fin1 | plant/bush | GOOD | - | **ACCEPT** | 32.3 | opus band GOOD (model said good); blocking []; polish ['WANTS_VARIANTS', 'SCALE_WRONG'] |
| RM_ToxiGrass | fin1 | plant/ground_cover | WEAK | regen | **HOLD_INPUT** | 82.9 | opus band WEAK (model said good); blocking ['DESC_MISS']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1'], own blocking ['DESC_MISS']; owner_kept not established by the spec (no art-ledger lookup): judged REGEN, NOT filed and no round counted — re-spec with fauna_spec.py |

Models reported: UNMEASURED, claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#3e1892+plant@v3#d69b4b`
