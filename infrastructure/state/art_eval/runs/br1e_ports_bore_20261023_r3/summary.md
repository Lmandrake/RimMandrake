# art_eval run br1e_ports_bore_20261023_r3

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_PumpingStation_Kludged | R1b | machine/pump | WEAK | strong_accept | **ACCEPT** | 62.1 | opus band WEAK (model said good); blocking []; polish []; unreadable ['ROTATIONS (n/a on an unconditional item)']; gpt strong_accept: unsettled [], own blocking [] |
| RM_HoseFreeEnd_Mouth | R2 | machine/hose | WEAK | regen | **REGEN** | 94.1 | opus band WEAK (model said weak); blocking ['DESC_MISS', 'BORE_PLANE']; polish []; unreadable ['ROTATIONS (n/a on an unconditional item)']; gpt regen: unsettled ['K1', 'K3'], own blocking ['DESC_MISS'] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+machine@v2#e06ee7`
