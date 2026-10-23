# art_eval run anchor_bollards_20261023_r2

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_SuspensionAnchor_Timber_Scrapper | A | machine/part | WEAK | regen | **REGEN** | 138.1 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'F_INCONSISTENT']; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)', 'ALPHA']; gpt regen: unsettled ['K1', 'K2', 'K4'], own blocking ['DESC_MISS', 'F_INCONSISTENT'] |
| RM_SuspensionAnchor_Steel_Scrapper | A | machine/part | WEAK | regen | **REGEN** | 175.5 | opus band WEAK (model said good); blocking ['DESC_MISS', 'LAYER_ORDER']; polish ['MATERIAL_PAINT', 'LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)', 'ALPHA']; gpt regen: unsettled ['K1', 'K4'], own blocking ['DESC_MISS'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+machine@v2#e06ee7`
