# art_eval run thf_20261103

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_TalusClasp |  | plant/bush | WEAK | strong_accept | **ACCEPT** | 49.9 | opus band WEAK (model said good); blocking ['STYLE_EARTHLY']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_QirraMat |  | plant/ground_cover | WEAK | regen | **HOLD_INPUT** | 84.2 | opus band WEAK (model said weak); blocking ['STYLE_EARTHLY', 'READS_KIND', 'STYLE_OFF']; polish ['WANTS_VARIANTS']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['STYLE_EARTHLY', 'DESC_MISS', 'STYLE_OFF']; owner_kept not established by the spec (no art-ledger lookup): judged REGEN, NOT filed and no round counted — re-spec with fauna_spec.py |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+plant@v3#bf05d6`
