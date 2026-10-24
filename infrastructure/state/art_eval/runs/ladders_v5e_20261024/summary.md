# art_eval run ladders_v5e_20261024

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_LadderSteel | A | machine/wall_mounted | WEAK | unsure | **REGEN** | 141.6 | opus band WEAK (model said good); blocking ['ALPHA_HALO']; polish ['LEGIB_32']; unreadable ['PORTS (n/a on an unconditional item)']; gpt unsure: unsettled ['K1'], own blocking ['ALPHA_HALO'] |
| RM_LadderPortable | A | machine/wall_mounted | WEAK | regen | **ESCALATE** | 107.1 | opus band WEAK (model said good); blocking ['OWNER_NOTE_IGNORED']; polish ['LEGIB_32']; unreadable ['BORE (n/a on an unconditional item)', 'PORTS (n/a on an unconditional item)', 'LAYERS (n/a on an unconditional item)']; gpt regen: unsettled ['K1', 'K4'], own blocking ['OWNER_NOTE_IGNORED']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_LadderPortable: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+machine@v3#c807af`
