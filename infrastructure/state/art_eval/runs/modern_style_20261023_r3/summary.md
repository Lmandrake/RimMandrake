# art_eval run modern_style_20261023_r3

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_UniversalPipe_Modern | r1 | machine/part | WEAK | unsure | **REGEN** | 104.3 | opus band WEAK (model said good); blocking ['STYLE_OFF', 'PORT_MISFIT']; polish ['MATERIAL_PAINT']; gpt unsure: unsettled ['K2'], own blocking [] |
| RM_LiquidPump_Modern | r1 | machine/pump | WEAK | unsure | **REGEN** | 95.4 | opus band WEAK (model said good); blocking []; polish ['LEGIB_32']; unreadable ['ROTATIONS (n/a on an unconditional item)']; gpt unsure: unsettled ['K1'], own blocking [] |
| RM_PipeFaucet_Modern | r1 | machine/part | WEAK | unsure | **REGEN** | 79.5 | opus band WEAK (model said good); blocking ['PORT_MISFIT']; polish ['LEGIB_32']; unreadable ['ROTATIONS (n/a on an unconditional item)']; gpt unsure: unsettled ['K1', 'K2'], own blocking [] |
| RM_HoseEnd_Modern | r1 | machine/hose | WEAK | unsure | **REGEN** | 115.4 | opus band WEAK (model said weak); blocking ['SIBLING_MISMATCH', 'DESC_MISS', 'OWNER_NOTE_IGNORED']; polish ['RES_LOW']; gpt unsure: unsettled ['K2'], own blocking [] |
| RM_SprinklerHead_Modern | r1 | machine/part | WEAK | unsure | **REGEN** | 82.9 | opus band WEAK (model said good); blocking ['PORT_MISFIT']; polish ['LEGIB_32']; unreadable ['ROTATIONS (n/a on an unconditional item)']; gpt unsure: unsettled ['K1', 'K2'], own blocking [] |
| RM_LiquidJoins_Modern | r1 | machine/coupler | WEAK | unsure | **REGEN** | 113.6 | opus band WEAK (model said weak); blocking ['PORT_MISFIT', 'CAM_WRONG']; polish ['LEGIB_32']; unreadable ['PORTS', 'LAYERS', 'ROTATIONS']; gpt unsure: unsettled ['K1', 'K2', 'K3', 'K4', 'K5'], own blocking [] |
| RM_PipeSpan_Modern | r1 | machine/part | WEAK | unsure | **REGEN** | 92.9 | opus band WEAK (model said weak); blocking ['PORT_MISFIT']; polish ['RES_LOW', 'MATERIAL_PAINT']; unreadable ['PORTS', 'LAYERS', 'ROTATIONS (n/a on an unconditional item)']; gpt unsure: unsettled ['K1', 'K2', 'K3', 'K4'], own blocking [] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+machine@v2#e06ee7`
