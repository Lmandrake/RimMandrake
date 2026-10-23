# art_eval run anchor_bollards_20261023_r3

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_SuspensionAnchor_Timber_Scrapper | A | machine/part | WEAK | unsure | **REGEN** | 157.3 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'F_INCONSISTENT']; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)', 'ALPHA']; gpt unsure: unsettled ['K1', 'K2', 'K4'], own blocking [] |
| RM_SuspensionAnchor_Steel_Scrapper | A | machine/part | WEAK | unsure | **REGEN** | 139.1 | opus band WEAK (model said weak); blocking ['PORT_MISFIT']; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_SuspensionAnchor_Timber_Industrial | A | machine/part | WEAK | regen | **REGEN** | 132.5 | opus band WEAK (model said good); blocking ['PORT_MISFIT']; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)']; gpt regen: unsettled ['K1'], own blocking ['PORT_MISFIT'] |
| RM_SuspensionAnchor_Steel_Industrial | A | machine/part | WEAK | regen | **REGEN** | 114.9 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'ALPHA_HALO']; polish []; unreadable ['BORE (n/a on an unconditional item)', 'ALPHA']; gpt regen: unsettled ['K1', 'K2', 'K4'], own blocking ['DESC_MISS'] |
| RM_SuspensionAnchor_Timber_Modern | A | machine/part | WEAK | unsure | **REGEN** | 110.7 | opus band WEAK (model said good); blocking []; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)']; gpt unsure: unsettled [], own blocking [] |
| RM_SuspensionAnchor_Steel_Modern | A | machine/part | WEAK | regen | **REGEN** | 143.2 | opus band WEAK (model said weak); blocking ['PORT_MISFIT', 'STYLE_CARTOON']; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)']; gpt regen: unsettled ['K2'], own blocking ['STYLE_CARTOON'] |
| RM_SuspensionAnchor_Timber_Futuristic | A | machine/part | WEAK | regen | **REGEN** | 131.9 | opus band WEAK (model said good); blocking ['DESC_MISS', 'PORT_MISFIT']; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)']; gpt regen: unsettled ['K2'], own blocking ['PORT_MISFIT'] |
| RM_SuspensionAnchor_Steel_Futuristic | A | machine/part | WEAK | unsure | **REGEN** | 125.5 | opus band WEAK (model said good); blocking ['DESC_MISS', 'DESC_MISS']; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)', 'ALPHA']; gpt unsure: unsettled ['K1', 'K2', 'K4'], own blocking [] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+machine@v2#e06ee7`
