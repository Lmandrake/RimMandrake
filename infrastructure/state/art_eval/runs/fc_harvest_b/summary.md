# art_eval run fc_harvest_b

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_Runyip | harvest | creature/swimmer | REALLY_BAD | - | **REGEN** | 55.6 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'F_TOPDOWN', 'F_SOUTH_NOT_FRONT', 'F_NORTH_FACE', 'STYLE_CARTOON', 'DONOR', 'CANON_MISS', 'ALPHA_HALO']; polish ['LEGIB_32'] |
| RM_Venomvine | harvest | plant/ground_cover | WEAK | strong_accept | **ACCEPT** | 49.0 | opus band WEAK (model said good); blocking ['STYLE_CARTOON']; polish ['WANTS_VARIANTS', 'LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
