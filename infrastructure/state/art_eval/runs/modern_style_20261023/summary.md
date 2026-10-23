# art_eval run modern_style_20261023

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_UniversalPipe_Modern | r1 | machine/part | REALLY_BAD | - | **REGEN** | 69.1 | opus band REALLY_BAD (model said weak); blocking ['DESC_MISS', 'DESC_MISS', 'DESC_MISS', 'F_INCONSISTENT']; polish ['MATERIAL_PAINT', 'LEGIB_32']; unreadable ['PORTS'] |
| RM_LiquidPump_Modern | r1 | machine/pump | WEAK | regen | **REGEN** | 121.5 | opus band WEAK (model said weak); blocking ['OWNER_NOTE_IGNORED', 'PORT_MISFIT', 'CAM_WRONG']; polish ['LEGIB_32']; unreadable ['ROTATIONS (n/a on an unconditional item)']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4'], own blocking ['OWNER_NOTE_IGNORED', 'F_MISSING'] |
| RM_LiquidJoins_Modern | r1 | machine/coupler | WEAK | unsure | **REGEN** | 134.5 | opus band WEAK (model said weak); blocking ['PORT_MISFIT', 'DESC_MISS', 'DESC_MISS', 'PORT_MISFIT']; polish ['LEGIB_32']; unreadable ['ROTATIONS (n/a on an unconditional item)']; gpt unsure: unsettled ['K1', 'K2', 'K3', 'K5'], own blocking ['DESC_MISS', 'PORT_MISFIT', 'F_MISSING'] |
| RM_PipeFaucet_Modern | r1 | machine/part | WEAK | regen | **REGEN** | 119.2 | opus band WEAK (model said weak); blocking ['OWNER_NOTE_IGNORED', 'PORT_MISFIT']; polish ['LEGIB_32']; unreadable ['PORTS', 'LAYERS']; gpt regen: unsettled ['K1', 'K2', 'K3', 'K4'], own blocking ['OWNER_NOTE_IGNORED', 'PORT_MISFIT'] |
| RM_SprinklerHead_Modern | r1 | machine/part | WEAK | unsure | **REGEN** | 82.3 | opus band WEAK (model said weak); blocking ['PORT_MISFIT']; polish ['LEGIB_32']; unreadable ['ROTATIONS (n/a on an unconditional item)']; gpt unsure: unsettled ['K1', 'K2'], own blocking ['PORT_MISFIT'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v1#140565+preamble@v1#a48502+regen_prompt_edit@v1#861700+severity@v3#950903+machine@v2#e06ee7`
